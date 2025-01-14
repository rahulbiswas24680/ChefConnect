from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_home, name='portal-home'),
    
    path('order-manage/', views.portal_order_management, name='portal-order-manage'),
    path('order-details/<int:order_id>/', views.order_details, name="order-details"),
    path('create-order/', views.create_order, name='create-order'),
    path('orders-history/', views.orders_history, name='orders-history'),
    path('orders-history-pdf-download/', views.order_history_pdf_download, name='orders-history-pdf-download'),

    path('recipes/', views.recipes, name='recipes'),
    path('add-recipe/', views.add_recipe, name='add-recipe'),
]