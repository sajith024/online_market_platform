from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Product
from online_market_product_api.models import OrderManagement
from .forms import ProductForm, EditProductForm


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect("home")
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})


def edit_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == "POST":
        form = EditProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = EditProductForm(instance=product)
    return render(
        request, "products/edit_product.html", {"form": form, "productId": pk}
    )


def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("home")
    return render(request, "delete_product.html", {"product": product})


def search_product(request):

    if request.method == "GET":
        search = request.GET["search"]
        if search:
            products = Product.objects.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        else:
            products = Product.objects.all()
        return render(request, "home/home.html", {"products": products})
    else:
        return redirect("home")


def filter_product(request):
    if request.method == "GET":
        min_price = request.GET["min"]
        max_price = request.GET["max"]
        if min_price and max_price:
            products = Product.objects.filter(
                Q(price__gte=parse_decimal(min_price))
                & Q(price__lte=parse_decimal(max_price))
            )
        elif min_price:
            products = Product.objects.filter(price__gte=parse_decimal(min_price))
        elif max_price:
            products = Product.objects.filter(price__lte=parse_decimal(max_price))
        else:
            products = Product.objects.all()
        return render(request, "home/home.html", {"products": products})
    else:
        return redirect("home")


def product_payment(request, pk):
    try:
        order = OrderManagement.objects.get(pk=pk)
    except OrderManagement.DoesNotExist:
        return redirect("home")

    return render(request, "payments/checkout.html", {"order": order})

def payment_success(request):
    return render(request, "payments/success.html")

def parse_decimal(value):
    return Decimal(value if value else 0)
