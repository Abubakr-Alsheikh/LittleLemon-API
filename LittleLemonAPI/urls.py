from django.urls import include, path
from rest_framework.routers import DefaultRouter
from LittleLemonAPI import views


router = DefaultRouter()
router.register(r'menu-items', views.MenuItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('groups/<str:group_name>/users', views.GroupViewSet.as_view(), name='group_users_list'),
    path('groups/<str:group_name>/users/<int:pk>', views.GroupViewSet.as_view(), name='group_users_detail'),
    path('cart/menu-items', views.CartViewSet.as_view(), name='cart_items'),
    path('orders', views.OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:orderId>', views.OrderRetrieveUpdateDestroyView.as_view(), name = 'order_retrieve_update_delete'),
]