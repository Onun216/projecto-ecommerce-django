from django.db import models
from django.contrib.auth.models import User


# Order é uma cópia do conteúdo do carrinho de compras
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField()
    total_quantity = models.PositiveIntegerField()
    status = models.CharField(
        default='C',
        max_length=1,
        choices=(
            ('A', 'Aproved'),
            ('C', 'Created'),
            ('R', 'Refused'),
            ('P', 'Pending'),
            ('S', 'Shiped'),
            ('F', 'Finalized'),
        )
    )

    def __str__(self):
        return f'Order Nr.{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    product_id = models.PositiveIntegerField()
    variation = models.CharField(max_length=255)
    variation_id = models.PositiveIntegerField()
    price = models.FloatField()
    price_promotional = models.FloatField(default=0)
    quantity = models.PositiveIntegerField()
    # CharField porque vamos procurar a imagem pelo nome do arquivo
    image = models.CharField(max_length=2000)

    def __str__(self):
        return f'Item {self.product} - Order {self.order}'

    class Meta:
        verbose_name = 'OrderItem'
        verbose_name_plural = 'OrderItems'

