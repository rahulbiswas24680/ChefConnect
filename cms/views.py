import io
from itertools import zip_longest

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from internal.models import *


def portal_home(request):
    return render(request, "cms/portal_dashboard.html")


def portal_order_management(request):
    orders = Order.objects.all()
    context = {"orders": orders}
    return render(request, "cms/portal_order_manage.html", context)


def order_details(request, order_id):
    order = Order.objects.prefetch_related("items__recipe").get(id=order_id)
    context = {"order": order}
    return render(request, "cms/order_details.html", context)


def create_order(request):
    if request.method == "POST":
        print(request.POST)

        # create order defaults if order data is not filled
        order = Order.objects.create(
            customer=request.user,
            total_price=0,
            order_status="pending",
            payment_status="unpaid",
            pickup_approx_time=None,
        )

        grouped_items = {}
        for key, value in request.POST.items():
            if key.startswith("item-"):
                # Extract the index and field name
                _, field, index = key.rsplit("-", 2)
                # Initialize dict for this index if not exists
                if index not in grouped_items:
                    grouped_items[index] = {}
                # Add the field value
                grouped_items[index][field] = value[0]

        # for index, item_data in grouped_items.items():
        #     OrderItem.objects.create(
        #         recipe=item_data['name'],
        #         quantity=item_data['qty'],
        #         order=order
        #     )

        messages.add_message(request, messages.SUCCESS, "Your order has been saved.")
    return render(request, "cms/order_form.html", context={})


def orders_history(request):
    return render(request, "cms/order_history.html")


def order_history_pdf_download(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Set up text styles
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Order History Report")

    # Set up column headers
    p.setFont("Helvetica-Bold", 12)
    y_position = height - 100
    col_positions = [50, 150, 250, 350, 450]

    headers = ["Order ID", "Customer", "Total Price", "Status", "Date"]
    for pos, header in zip(col_positions, headers):
        p.drawString(pos, y_position, header)

    # Get data from database
    orders = Order.objects.all().select_related("customer")

    # Add data rows
    p.setFont("Helvetica", 10)
    y_position -= 20

    for order in orders:
        # Check if we need a new page
        if y_position < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y_position = height - 100

        # Draw each column
        p.drawString(col_positions[0], y_position, str(order.id))
        p.drawString(col_positions[1], y_position, str(order.customer))
        p.drawString(col_positions[2], y_position, f"${order.total_price}")
        p.drawString(col_positions[3], y_position, order.order_status)
        p.drawString(
            col_positions[4], y_position, order.created_at.strftime("%Y-%m-%d")
        )

        y_position -= 20

    # Close the PDF object cleanly
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(
        buffer, content_type="application/pdf", filename="order_history.pdf"
    )


##### manage resources views


def recipes(request):
    first_recipes = Recipe.objects.filter(is_active=True)[:5]

    new_recipes_qs = Recipe.objects.filter(is_active=True).order_by("-created_at")
    new_grouped_recipes = group_recipes(new_recipes_qs, 4)

    popular_recipes_qs = Recipe.objects.filter(
        categories__name="Popular", is_active=True
    ).order_by("-created_at")
    popular_grouped_recipes = group_recipes(popular_recipes_qs, 4)

    context = {
        "first_recipes": first_recipes,
        "new_recipes": new_grouped_recipes,
        "popular_recipes": popular_grouped_recipes,
    }

    return render(request, "cms/resources/recipes.html", context)

def add_recipe(request):
    if request.method == "POST":
        # Handle form submission
        title = request.POST.get("title")
        slug = request.POST.get("slug")
        price = request.POST.get("price")
        discount = request.POST.get("discount")
        discount_price = request.POST.get("discount_price")
        servings = request.POST.get("servings")
        categories = request.POST.getlist("categories[]")
        description = request.POST.get("description")
        instructions = request.POST.get("instructions")
        rating = request.POST.get("rating")
        active = request.POST.get("active")
        image = request.FILES.get("image")

        if not title or not price:
            messages.error(request, "Title and Price are required fields!")
            return render(request, "cms/resources/add_recipe.html", {
                "form_data": request.POST,
            })
        
        # Create a new recipe instance with only valid fields
        recipe = Recipe(
            title=title,
            slug=slug,
            price=price,
            discount_price=discount_price,
            servings=servings,
            description=description,
            instructions=instructions,
            average_rating=rating,
            is_active=bool(active),
            discount_percentage=discount,
            image=image,
            created_by=request.user if request.user.is_authenticated else None,
            modified_by=request.user if request.user.is_authenticated else None
        )
        recipe.save()
        
        # Add categories after saving since it's a many-to-many field
        if categories:
            recipe.categories.set(categories)        

        messages.success(request, "Recipe added successfully!")
        return redirect("recipes")
    return render(request, "cms/resources/add_recipe.html")


def group_recipes(iterable, n):
    """Groups an iterable into chunks of size n."""
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=None)
