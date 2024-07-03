from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from product.models import Variation
from .models import Order, OrderItem

from utils import utils


class DispatchLoginRequiredMixin(View):
    """
    Impede que utilizadores vejam pedidos de outros utilizadores. 
    """
    # Sobrescrever o método dispatch() de Class View

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('user_profile:create')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        """
        Método impede que se aceda a pedidos de outros utilizadores
        """
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(user=self.request.user)
        return qs


class SaveOrder(View):
    template_name = 'order/pay.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Tem que ter sessão iniciada para efectuar a compra!'
            )
            return redirect('user_profile:create')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('product:list')

        cart = self.request.session.get('cart')
        cart_variation_ids = [v for v in cart]
        # print(cart_variation_ids)

        # .select_related reduz o número de consultas na base de dados
        bd_variations = list(
            Variation.objects.select_related('product').filter(id__in=cart_variation_ids))
        # print(bd_variations)

        for variation in bd_variations:
            vid = str(variation.id)

            stock = variation.stock
            quantity_in_cart = cart[vid]['quantity']
            price = cart[vid]['unit_price']
            price_promo = cart[vid]['unit_price_promotional']

            error_msg_stock = ''

            if stock < quantity_in_cart:
                cart[vid]['quantity'] = stock
                cart[vid]['unit_price'] = stock * price
                cart[vid]['unit_price_promotional'] = stock * price_promo

                error_msg_stock = 'Stock insuficiente para alguns produtos. ' \
                                  'Reduzimos a quantidade desses produtos no seu carrinho.'

            if error_msg_stock:
                messages.error(
                    self.request,
                    error_msg_stock
                )
                self.request.session.save()
                return redirect('product:cart')

        total_cart_quantity = utils.cart_total_qt(cart)
        total_cart_price = utils.cart_totals(cart)

        order = Order(
            user=self.request.user,
            total=total_cart_price,
            total_quantity=total_cart_quantity,
            status='C',
        )
        order.save()

        # .bulk_create cria vários objectos de uma só vez
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=v['product_name'],
                    product_id=v['product_id'],
                    variation=v['variation_name'],
                    variation_id=v['variation_id'],
                    price=v['unit_price'],
                    price_promotional=v['unit_price_promotional'],
                    quantity=v['quantity'],
                    image=v['image'],


                ) for v in cart.values()
            ]
        )

        del self.request.session['cart']
        return redirect(
            reverse(
                'order:pay',
                kwargs={
                    'pk': order.pk
                }
            )
        )


class Pay(DispatchLoginRequiredMixin, DetailView):
    template_name = 'order/pay.html'
    model = Order
    pk_url_kwarg = 'pk'
    context_object_name = 'order'


class OrderDetail(DispatchLoginRequiredMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'order/detail.html'
    pk_url_kwarg = 'pk'


class Orders(DispatchLoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'order/orders.html'
    paginate_by = 10
    ordering = ['-id']

