"""
File: app/routes/customer.py
Description: Customer-facing routes for the Multi-Brand Clothing Sales Platform.
             Handles product browsing, cart management, checkout, and reviews.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.controllers.product_controller import ProductController
from app.controllers.cart_controller import CartController
from app.controllers.order_controller import OrderController
from app.controllers.review_controller import ReviewController


customer_bp = Blueprint('customer', __name__, url_prefix='/customer')


@customer_bp.route('/catalog', methods=['GET'])
def catalog():
    """
    Display product catalog with search and filtering capabilities.
    Allows browsing products by category, price range, and availability.
    """
    category = request.args.get('category')
    only_available = request.args.get('available', 'true').lower() == 'true'
    
    if category:
        products = ProductController.list_products_by_category(category, only_available=only_available)
    else:
        products = []
    
    return render_template('customer/catalog.html', products=products, category=category)


@customer_bp.route('/product/<product_id>', methods=['GET'])
def product_detail(product_id):
    """
    Display detailed product information including SKU variants and reviews.
    Shows product description, available sizes/colors, and customer reviews.
    """
    product = ProductController.get_product_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('customer.catalog'))
    
    reviews = ReviewController.get_reviews_for_product(product)
    average_rating = ReviewController.get_average_rating_for_product(product)
    
    return render_template(
        'customer/product_detail.html',
        product=product,
        reviews=reviews,
        average_rating=average_rating
    )


@customer_bp.route('/cart', methods=['GET'])
@login_required
@role_required('customer')
def view_cart():
    """
    Display the customer's shopping cart with all items and total.
    Shows quantity, price per item, and calculated totals.
    """
    cart = CartController.get_or_create_active_cart(current_user)
    total = CartController.calculate_cart_total(cart)
    
    return render_template('customer/cart.html', cart=cart, total=total)


@customer_bp.route('/cart/add', methods=['POST'])
@login_required
@role_required('customer')
def add_to_cart():
    """
    Add a product SKU to the shopping cart.
    Accepts sku_id and quantity from form data.
    """
    sku_id = request.form.get('sku_id')
    quantity = request.form.get('quantity', 1, type=int)
    
    if not sku_id:
        flash('Invalid product selection.', 'danger')
        return redirect(request.referrer or url_for('customer.catalog'))
    
    try:
        cart = CartController.get_or_create_active_cart(current_user)
        CartController.add_item_to_cart(cart, sku_id, quantity)
        flash('Item added to cart successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Failed to add item to cart.', 'danger')
    
    return redirect(request.referrer or url_for('customer.view_cart'))


@customer_bp.route('/cart/update', methods=['POST'])
@login_required
@role_required('customer')
def update_cart():
    """
    Update the quantity of an item in the cart.
    Accepts sku_id and new quantity.
    """
    sku_id = request.form.get('sku_id')
    quantity = request.form.get('quantity', 0, type=int)
    
    if not sku_id:
        flash('Invalid item selection.', 'danger')
        return redirect(url_for('customer.view_cart'))
    
    try:
        cart = CartController.get_or_create_active_cart(current_user)
        CartController.update_item_quantity(cart, sku_id, quantity)
        flash('Cart updated successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash('Failed to update cart.', 'danger')
    
    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/cart/remove/<sku_id>', methods=['POST'])
@login_required
@role_required('customer')
def remove_from_cart(sku_id):
    """
    Remove an item from the shopping cart.
    Accepts sku_id as URL parameter.
    """
    try:
        cart = CartController.get_or_create_active_cart(current_user)
        success = CartController.remove_item_from_cart(cart, sku_id)
        
        if success:
            flash('Item removed from cart.', 'success')
        else:
            flash('Item not found in cart.', 'warning')
    except Exception as e:
        flash('Failed to remove item from cart.', 'danger')
    
    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def checkout():
    """
    Handle checkout process for converting cart to order.
    GET: Display checkout form with cart summary.
    POST: Process order creation and payment.
    """
    cart = CartController.get_or_create_active_cart(current_user)
    
    if not cart.items or len(cart.items) == 0:
        flash('Your cart is empty. Add items before checking out.', 'warning')
        return redirect(url_for('customer.catalog'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if not payment_method:
            flash('Please select a payment method.', 'danger')
            return render_template('customer/checkout.html', cart=cart)
        
        try:
            order = OrderController.create_order_from_cart(current_user, cart)
            
            transaction_id = f"TXN-{order.id[:8]}"
            OrderController.attach_payment_record(
                order,
                amount=order.total_amount,
                method=payment_method,
                transaction_id=transaction_id
            )
            
            flash(f'Order placed successfully! Order ID: {order.id}', 'success')
            return redirect(url_for('customer.order_history'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('Failed to process checkout. Please try again.', 'danger')
    
    total = CartController.calculate_cart_total(cart)
    return render_template('customer/checkout.html', cart=cart, total=total)


@customer_bp.route('/orders', methods=['GET'])
@login_required
@role_required('customer')
def order_history():
    """
    Display customer's order history.
    Shows all past orders with status and details.
    """
    orders = OrderController.get_orders_for_customer(current_user)
    return render_template('customer/order_history.html', orders=orders)


@customer_bp.route('/product/<product_id>/review', methods=['POST'])
@login_required
@role_required('customer')
def submit_review(product_id):
    """
    Submit a product review with rating and optional comment.
    Customers can only review products once.
    """
    product = ProductController.get_product_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('customer.catalog'))
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5 stars).', 'danger')
        return redirect(url_for('customer.product_detail', product_id=product_id))
    
    try:
        ReviewController.add_review(current_user, product, rating, comment)
        flash('Thank you for your review!', 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception as e:
        flash('Failed to submit review. Please try again.', 'danger')
    
    return redirect(url_for('customer.product_detail', product_id=product_id))
