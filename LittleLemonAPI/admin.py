from django.contrib import admin

from LittleLemonAPI.models import Cart, MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')  # Customize the fields displayed in the list view

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menuitem', 'quantity', 'price')  # Customize the fields displayed in the list view
    list_filter = ('user',)  # Add a filter for the 'user' field