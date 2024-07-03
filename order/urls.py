from django.urls import path
from . import views


app_name = 'order'

urlpatterns = [
    path('pay/<int:pk>', views.Pay.as_view(), name='pay'),
    path('saveorder/', views.SaveOrder.as_view(), name='saveorder'),
    path('orders/', views.Orders.as_view(), name='orders'),
    path('orderdetail/<int:pk>', views.OrderDetail.as_view(), name='orderdetail'),
]
