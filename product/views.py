from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

from . import models
from user_profile.models import Profile


from pprint import pprint


class ProductList(ListView):
    model = models.Product  # QuerySet
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    ordering = ['-id']


class Search(ProductList):
    def get_queryset(self, *args, **kwargs):
        term = self.request.GET.get('term') or self.request.session['term']
        qs = super().get_queryset(*args, **kwargs)

        if not term:
            return qs
        
        self.request.session['term'] = term

        qs = qs.filter(
            Q(name__icontains=term) |
            Q(description_short__icontains=term) |
            Q(description_long__icontains=term)
        )

        self.request.session.save()

        return qs


class ProductDetail(DetailView):
    model = models.Product  # QuerySet
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


class AddToCart(View):
    def get(self, *args, **kwargs):
        """
        # Em caso de necessidade, código apaga o carrinho e o respectivo conteúdo
        if self.request.session.get('cart'):
            del self.request.session['cart']
            self.request.session.save()
        """

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:list')
        )
        variation_id = self.request.GET.get('vid')

        if not variation_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variation = get_object_or_404(models.Variation, id=variation_id)
        variation_stock = variation.stock
        product = variation.product

        # variation_id declarada antes
        product_id = product.id
        product_name = product.name
        variation_name = variation.name or ''
        unit_price = variation.price
        unit_price_promotional = variation.price_promotional
        quantity = 1
        slug = product.slug
        image = product.image

        if image:
            image = image.name
        else:
            image = ''

        if variation.stock < 1:
            messages.error(
                self.request,
                "Stock insuficiente"
            )
            return redirect(http_referer)

        # Se a chave 'cart' não existir na sessão, é criada
        if not self.request.session.get('cart'):
            self.request.session['cart'] = {}
            self.request.session.save()

        cart = self.request.session['cart']

        if variation_id in cart:
            current_cart_quantity = cart[variation_id]['quantity']
            current_cart_quantity += 1

            if variation_stock < current_cart_quantity:
                messages.warning(
                    self.request,
                    f'Stock insuficiente para {current_cart_quantity}x no produto "{product.name}". Foram adicionados {variation_stock}x ao carrinho.'
                )
                current_cart_quantity = variation_stock

            print('QUANTIDADE: ', current_cart_quantity)

            cart[variation_id]['quantity'] = current_cart_quantity
            cart[variation_id]['unit_price'] = unit_price * \
                current_cart_quantity
            cart[variation_id]['unit_price_promotional'] = unit_price_promotional * \
                current_cart_quantity

        else:
            cart[variation_id] = {
                'product_id': product_id,
                'product_name': product_name,
                'variation_name': variation_name,
                'variation_id': variation_id,
                'unit_price': unit_price,
                'unit_price_promotional': unit_price_promotional,
                'quantity': 1,
                'slug': slug,
                'image': image,
            }
        self.request.session.save()
        messages.success(
            self.request,
            f'Produto {product_name} {variation_name} adicionado ao '
            f'carrinho {cart[variation_id]["quantity"]}x. '
        )

        # pprint(cart)

        # return HttpResponse(f'{variation.product} {variation.name}')
        return redirect(http_referer)


class RemoveFromCart(ListView):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:list')
        )

        variation_id = self.request.GET.get('vid')

        if not variation_id:
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            return redirect(http_referer)

        if variation_id not in self.request.session['cart']:
            return redirect(http_referer)

        cart = self.request.session['cart'][variation_id]

        messages.success(
            self.request,
            f'Produto {cart["product_name"]} {cart["variation_name"]} removido do carrinho.'
        )

        del self.request.session['cart'][variation_id]
        self.request.session.save()

        return redirect(http_referer)


class Cart(ListView):
    def get(self, *args, **kwargs):
        context = {
            'cart': self.request.session.get('cart', {}),
        }
        return render(self.request, 'products/cart.html', context)


class OrderSummary(ListView):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('user_profile:create')

        profile = Profile.objects.filter(user=self.request.user).exists()
        # print('PERFIL EXISTE', profile)

        if not profile:
            messages.error(
                self.request,
                'Utilizador sem perfil.'
            )
            return redirect('user_profile:create')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('product:list')

        context = {
            'user': self.request.user,
            'cart': self.request.session['cart'],

        }

        return render(self.request, 'products/order_summary.html', context)
