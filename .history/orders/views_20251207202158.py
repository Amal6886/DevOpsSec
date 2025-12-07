from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from products.models import Supplement, ProteinBar

from .models import Order, OrderItem


@login_required
def add_to_cart(request, product_type, product_id):
    if product_type == 'supplement':
        product = get_object_or_404(Supplement, pk=product_id)
    elif product_type == 'protein_bar':
        product = get_object_or_404(ProteinBar, pk=product_id)
    else:
        messages.error(request, 'Invalid product type.')
        return redirect('products:product_list')

    if product.stock_quantity <= 0:
        messages.error(request, 'This product is out of stock.')
        return redirect('products:product_list')

    if 'cart' not in request.session:
        request.session['cart'] = []

    cart = request.session['cart']

    for item in cart:
        if item.get('type') == product_type and item.get('id') == product_id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'type': product_type,
            'id': product_id,
            'quantity': 1
        })

    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products:product_list')


@login_required
def view_cart(request):
    cart_items = []
    cart_total = 0

    if 'cart' in request.session:
        for item in request.session['cart']:
            product_type = item.get('type')
            product_id = item.get('id')
            quantity = item.get('quantity', 1)

            if product_type == 'supplement':
                try:
                    product = Supplement.objects.get(id=product_id)
                    item_total = float(product.price) * quantity
                    cart_items.append({
                        'product': product,
                        'type': 'supplement',
                        'quantity': quantity,
                        'total': item_total
                    })
                    cart_total += item_total
                except Supplement.DoesNotExist:
                    continue
            elif product_type == 'protein_bar':
                try:
                    product = ProteinBar.objects.get(id=product_id)
                    item_total = float(product.price) * quantity
                    cart_items.append({
                        'product': product,
                        'type': 'protein_bar',
                        'quantity': quantity,
                        'total': item_total
                    })
                    cart_total += item_total
                except ProteinBar.DoesNotExist:
                    continue

    context = {
        'cart_items': cart_items,
        'cart_total': round(cart_total, 2),
    }
    return render(request, 'orders/cart.html', context)


@login_required
def remove_from_cart(request, product_type, product_id):
    if 'cart' in request.session:
        cart = request.session['cart']
        request.session['cart'] = [item for item in cart
                                   if not (item.get('type') == product_type and item.get('id') == product_id)]
        messages.success(request, 'Item removed from cart.')
    return redirect('orders:view_cart')


@login_required
def update_cart_quantity(request, product_type, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            return remove_from_cart(request, product_type, product_id)

        if 'cart' in request.session:
            cart = request.session['cart']
            for item in cart:
                if item.get('type') == product_type and item.get('id') == product_id:
                    item['quantity'] = quantity
                    break
            request.session['cart'] = cart

    return redirect('orders:view_cart')


@login_required
def checkout(request):
    if 'cart' not in request.session or not request.session['cart']:
        messages.error(request, 'Your cart is empty.')
        return redirect('orders:view_cart')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone = request.POST.get('phone')

        if not shipping_address or not phone:
            messages.error(request, 'Please provide shipping address and phone number.')
            return render(request, 'orders/checkout.html')

        cart = request.session['cart']
        total_amount = 0
        order_items_data = []

        for item in cart:
            product_type = item.get('type')
            product_id = item.get('id')
            quantity = item.get('quantity', 1)

            if product_type == 'supplement':
                try:
                    product = Supplement.objects.get(id=product_id)
                    if product.stock_quantity < quantity:
                        messages.error(request, f'Insufficient stock for {product.name}.')
                        return redirect('orders:view_cart')
                except Supplement.DoesNotExist:
                    continue
            elif product_type == 'protein_bar':
                try:
                    product = ProteinBar.objects.get(id=product_id)
                    if product.stock_quantity < quantity:
                        messages.error(request, f'Insufficient stock for {product.name}.')
                        return redirect('orders:view_cart')
                except ProteinBar.DoesNotExist:
                    continue
            else:
                continue

            item_total = float(product.price) * quantity
            total_amount += item_total
            order_items_data.append({
                'product': product,
                'product_type': product_type,
                'quantity': quantity,
                'price': product.price
            })

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=shipping_address,
            phone=phone
        )

        for item_data in order_items_data:
            if item_data['product_type'] == 'supplement':
                OrderItem.objects.create(
                    order=order,
                    supplement=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                item_data['product'].stock_quantity -= item_data['quantity']
                item_data['product'].save()
            elif item_data['product_type'] == 'protein_bar':
                OrderItem.objects.create(
                    order=order,
                    protein_bar=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                item_data['product'].stock_quantity -= item_data['quantity']
                item_data['product'].save()

        request.session['cart'] = []

        try:
            send_mail(
                'Order Confirmation',
                f'Hi {request.user.username},\n\nYour order #{order.id} has been placed successfully.\nTotal Amount: ${order.total_amount}\n\nThank you for your purchase!',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        except (ConnectionError, TimeoutError, OSError):
            # Email sending failed, but don't block order creation
            pass

        messages.success(request, f'Order placed successfully! Order ID: #{order.id}')
        return redirect('orders:order_detail', order_id=order.id)

    return render(request, 'orders/checkout.html')


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/order_list.html', {'orders': orders})


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_order_list(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'orders/admin/order_list.html', {'orders': orders})


@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/admin/order_detail.html', {'order': order})


@user_passes_test(is_admin)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            messages.success(request, 'Order status updated successfully!')
    return redirect('orders:admin_order_detail', order_id=order.id)
