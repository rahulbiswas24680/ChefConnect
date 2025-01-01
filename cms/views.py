from django.shortcuts import render
from internal.models import Recipe, Order

def portal_home(request):
    return render(request, 'cms/portal_dashboard.html')

def portal_order_management(request):
    orders = Order.objects.all()
    context = {
        'orders': orders
    }
    return render(request, 'cms/portal_order_manage.html', context)

def order_details(request, order_id):
    order = Order.objects.prefetch_related('items__recipe').get(id=order_id)
    context = {
        'order': order
    }
    return render(request, 'cms/order_details.html', context)

def create_order(request):
    return render(request, 'cms/order_form.html', context={})

def orders_history(request):
    return render(request, 'cms/order_history.html')



##### manage resources views

def recipes(request):
    first_recipes = Recipe.objects.filter(is_active=True)[:5]
    new_recipes = Recipe.objects.filter(is_active=True).order_by('-created_at')[:5]
    popular_recipes = Recipe.objects.filter(categories__name='Popular', is_active=True).order_by('-created_at')[:5]
    context = {
        'first_recipes': first_recipes,
        'new_recipes': new_recipes,
        'popular_recipes': popular_recipes,
    }

    return render(request, 'cms/resources/recipes.html', context)