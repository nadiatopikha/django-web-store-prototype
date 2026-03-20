from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin

def home(request, category_name=None):
    categories = Category.objects.all()
    selected_category = None

    if category_name:
        selected_category = get_object_or_404(Category, name=category_name)
        products = Product.objects.filter(category=selected_category)
    else:
        products = Product.objects.all()

    return render(request, 'home.html', {'categories': categories, 'selected_category': selected_category, 'products': products})

def home_with_category(request, category_name):
    categories = Category.objects.all()
    selected_category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=selected_category)
    
    return render(request, 'home.html', {'categories': categories, 'selected_category': selected_category, 'products': products})

def about(request):
    return render(request, 'about.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserSignUpForm()
    return render(request, 'signup.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = CustomUserLoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('home') 

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.success_url)
        else:
            form.add_error(None, "Неправильна електронна пошта або пароль")
            return self.form_invalid(form)
        
def search_results(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'products': products, 'query': query})

def upload_image(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = ProductForm()

    return render(request, 'upload_image.html', {'form': form})

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

def products_by_category(request, category_name):
    category = Category.objects.get(name=category_name)
    products = Product.objects.filter(category=category)
    return render(request, 'products_by_category.html', {'products': products, 'category': category})

class CartView(View):
    template_name = 'cart.html'

    def get(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user)
        total_price = sum(item.total_price() for item in cart_items)
        return render(request, self.template_name, {'cart_items': cart_items, 'total_price': total_price})

    def post(self, request):
        # Отримання ідентифікатора товару, який користувач хоче видалити
        product_id = request.POST.get('product_id')
        
        CartItem.objects.filter(cart__user=request.user, product__id=product_id).delete()

        return redirect('cart')

def update_cart(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(
        cart__user=request.user,
        product_id=product_id,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart')


class CheckoutView(View):
    template_name = 'checkout.html'

    def get(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user)
        order = Order.objects.create(user=request.user)

        # Додавання товарів до замовлення
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price()
            )

        # Очистка кошика
        CartItem.objects.filter(cart__user=request.user).delete()

        return redirect('cart')

class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        user_info = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }

        form = CustomUserChangeForm(instance=request.user)
        orders = Order.objects.filter(user=request.user)

        return render(request, self.template_name, {'user_info': user_info, 'form': form, 'orders': orders})

    def post(self, request):
        form = CustomUserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')

            if password:
                user.set_password(password)
                update_session_auth_hash(request, user) 

            user.save()
            return redirect('profile')
        else:
            messages.error(request, 'Виникла помилка. Будь ласка, перевірте введені дані.')

        return render(request, self.template_name, {'form': form})
        
def add_to_cart(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    
    # Знаходимо чи вже є товар в кошику користувача
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={'quantity': 0}  
    )

    cart_item.quantity = quantity
    cart_item.save()

    return redirect('cart')


