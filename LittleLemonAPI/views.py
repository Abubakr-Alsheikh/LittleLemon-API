from LittleLemonAPI.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group, User
from .serializers import (
    CartSerializer,
    MenuItemSerializer,
    OrderItemSerializer,
    OrderSerializer,
    UserSerializer,
)
from .models import Cart, MenuItem, Order, OrderItem
from .permissions import (
    IsCustomer,
    IsManager,
    IsManagerOrDeliveryCrew,
    IsManagerOrReadOnly,
)
from django.db.models import Sum, F

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']  # Search by title field
    ordering_fields = ['title', 'price'] # Fields for sorting
    ordering = ['title']

    pagination_class = PageNumberPagination
    pagination_class.page_size = 10


class GroupViewSet(
    generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView
):

    permission_classes = [IsManager]
    allowed_methods = ["GET", "POST", "DELETE"]
    serializer_class = UserSerializer

    def get_queryset(self):
        group_name = self.kwargs["group_name"]

        if group_name == "manager":
            queryset = User.objects.filter(groups__name="Manager")
        elif group_name == "delivery-crew":
            queryset = User.objects.filter(groups__name="Delivery Crew")
        else:
            queryset = User.objects.none()

        return queryset

    def post(self, request, *args, **kwargs):
        group_name = self.kwargs["group_name"]

        try:
            user = User.objects.get(pk=request.data.get("user_id"))

            if group_name == "manager":
                group, created = Group.objects.get_or_create(name="Manager")
            elif group_name == "delivery-crew":
                group, created = Group.objects.get_or_create(name="Delivery Crew")
            else:
                return Response(
                    {"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND
                )

            group.user_set.add(user)
            return Response(
                self.get_serializer(user).data, status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, *args, **kwargs):
        group_name = self.kwargs["group_name"]

        user_id = self.kwargs["pk"]
        try:
            user = User.objects.get(pk=user_id)

            if group_name == "manager":
                group = Group.objects.get(name="Manager")
            elif group_name == "delivery-crew":
                group = Group.objects.get(name="Delivery Crew")
            else:
                return Response(
                    {"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND
                )

            if group and user.groups.filter(name=group.name).exists():
                group.user_set.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "User not found in this group"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CartViewSet(
    generics.ListAPIView, generics.CreateAPIView, generics.DestroyAPIView
):

    permission_classes = [IsCustomer]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        menuitem_id = int(
            request.data.get("menuitem")
        )  # menuitem id in request to add to cart
        quantity = int(request.data.get("quantity"))

        if not menuitem_id:
            return Response(
                {"error": "menuitem ID required"}, status=status.HTTP_400_BAD_REQUEST
            )  # check if menuitem id is provided

        if not quantity:
            quantity = 1  # if quantity not provided, default to 1

        try:
            menu_item = MenuItem.objects.get(
                pk=menuitem_id
            )  # fetch menu item to get price
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "MenuItem not found"}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item_data = {
            "user": request.user.id,
            "menuitem": menuitem_id,
            "quantity": quantity,
            "unit_price": menu_item.price,
            "price": menu_item.price * quantity,
        }
        print(cart_item_data)
        serializer = self.get_serializer(data=cart_item_data)  # serialize cart data
        serializer.is_valid(raise_exception=True)

        # Now save the cart item with all fields correctly populated
        cart_item = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):

        Cart.objects.filter(user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = (
        Order.objects.all().select_related("user").prefetch_related("order_items")
    )
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'delivery_crew__username', 'status']
    ordering_fields = ['status', 'total', 'date']
    ordering = ['-date']

    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get_queryset(self):

        # customers can only view their orders, delivery crew only theirs and manager can view all
        if self.request.user.groups.filter(name="Customer").exists():
            return (
                Order.objects.filter(user=self.request.user)
                .select_related("user")
                .prefetch_related("order_items")
            )
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            return (
                Order.objects.filter(delivery_crew=self.request.user)
                .select_related("user")
                .prefetch_related("order_items")
            )

        elif self.request.user.groups.filter(name="Manager").exists():
            return (
                Order.objects.all()
                .select_related("user")
                .prefetch_related("order_items")
            )

        else:  # return empty queryset for other groups
            return Order.objects.none()

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"message": "No item in cart"}, status=status.HTTP_400_BAD_REQUEST
            )

        order_total = cart_items.aggregate(total=Sum(F("quantity") * F("unit_price")))[
            "total"
        ]

        order = Order.objects.create(user=request.user, total=order_total)
        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
            for item in cart_items
        ]

        OrderItem.objects.bulk_create(order_items)  # creating order items
        cart_items.delete()  # deleting the items from cart

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Order.objects.all().select_related("user").prefetch_related("order_items")
    )
    serializer_class = OrderSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "orderId"

    def get_permissions(self):  # Dynamically determine permissions
        if self.request.method == 'GET':
            self.permission_classes = [permissions.IsAuthenticated]  # Allow any authenticated user to GET
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsManagerOrDeliveryCrew]
        elif self.request.method == 'DELETE':
             self.permission_classes = [IsManager]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):  # retrieve order by order ID
        instance = self.get_object()

        if (
            request.user.groups.filter(name="Customer").exists()
            and instance.user != request.user
        ):  # check if current user is the customer who created the order
            return Response(
                {"message": "You do not have permission to access this order"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.groups.filter(name='Manager').exists():
            serializer = self.get_serializer(instance) # all fields will be shown if manager is requesting
        else:
            serializer = OrderItemSerializer(instance.order_items, many=True) # only order items are displayed

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):  # order update
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if request.user.groups.filter(name="Manager").exists():
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )  # partial updates using PATCH
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        elif request.user.groups.filter(
            name="Delivery Crew"
        ).exists():  # only status can be updated by the delivery crew
            if "status" in request.data:
                instance.status = request.data["status"]
                instance.save()

                return Response(self.get_serializer(instance).data)
            else:
                return Response(
                    {"message": "You can only update order status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:  # any other groups apart from manager and delivery crew do not have permissions to update the order
            return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):  # manager can delete order
        if request.user.groups.filter(name="Manager").exists():
            return super().destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
