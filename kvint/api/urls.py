from django.urls import path
from .views import OrderViewSet

order_list = OrderViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    path('v1/', order_list)
]
