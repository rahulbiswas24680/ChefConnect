from django.contrib import admin
from .models import Recipe, Category, Review, Order, OrderItem


admin.site.register(Recipe)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)

