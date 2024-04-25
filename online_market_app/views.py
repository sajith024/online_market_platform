from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import SignupForm, LoginForm
from online_market_product.models import Product


def default_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return redirect("login")


@login_required
def home(request):
    if request.user.role.name == "Seller":
        products = Product.objects.filter(user=request.user)
    else:
        products = Product.objects.all()
    token = request.session.get("token")
    return render(request, "home/home.html", {"products": products, "token": token})


def user_signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token = RefreshToken.for_user(user)
                request.session["token"] = str(token.access_token)
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password")

    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")
