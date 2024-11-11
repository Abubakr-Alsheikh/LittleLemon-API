from django.db import models
from django.contrib.auth.models import User

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)


    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    menuitem = models.ForeignKey("MenuItem", on_delete=models.CASCADE)  # Link to a MenuItem (adjust if necessary)
    quantity = models.SmallIntegerField(default=1)  # Add a quantity field
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('user', 'menuitem')  # Prevent duplicate items per cart

    def __str__(self):
        return f"{self.user.username}'s cart - {self.menuitem.title} x {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="delivery_crew", null=True, blank=True)
    status = models.BooleanField(default=False) # status=False, order placed, status=True, order delivered
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0) # to store the sum of prices of all order items
    date = models.DateField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='order_items', on_delete=models.CASCADE)
    menuitem = models.ForeignKey("MenuItem", on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)