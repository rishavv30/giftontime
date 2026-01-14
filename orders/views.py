from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def home(request):
    if request.method == "POST":
        Order.objects.create(
            product_link=request.POST.get('product_link'),
            delivery_date=request.POST.get('delivery_date'),
            delivery_time=request.POST.get('delivery_time'),
            address=request.POST.get('address'),
        )
        return redirect('success' , order_id=order.id)

    return render(request, 'home.html')


def success(request, order_id):
    return render(request, 'success.html', {'order_id': order_id})

@login_required
def create_order(request):
    if request.method == "POST":
        Order.objects.create(
            user=request.user,
            product_link=request.POST.get('product_link'),
            delivery_date=request.POST.get('delivery_date'),
            delivery_time=request.POST.get('delivery_time'),
            address=request.POST.get('address'),
        )
        return redirect('dashboard')

    return render(request, 'create_order.html')

def track_order(request):
    order = None
    error = None

    if request.method == "POST":
        order_id = request.POST.get('order_id')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            error = "Order not found. Please check your Order ID."

    return render(request, 'track.html', {
        'order': order,
        'error': error
    })




def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Account already exists.")
            return redirect("signup")

        user = User.objects.create_user(
            username=email,   # 🔑 KEY FIX
            email=email,
            password=password1
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "auth/signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid credentials")
        return redirect("login")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("landing")



@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'orders': orders})

def landing(request):
    return render(request, 'landing.html')
