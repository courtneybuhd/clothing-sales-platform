"""
File: app/routes/vendor.py
Description: Vendor portal routes for managing products.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.controllers.product_controller import ProductController
from app.models.product import Product


vendor_bp = Blueprint('vendor', __name__, url_prefix='/vendor')


@vendor_bp.route('/dashboard', methods=['GET'])
@login_required
@role_required('vendor')
def dashboard():
    """
    Vendor dashboard displaying all products owned by the logged-in vendor.
    Shows product list with options to create, edit, or delete products.
    """
    products = ProductController.list_vendor_products(current_user)
    return render_template('vendor/dashboard.html', products=products)


@vendor_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def create_product():
    """
    Create a new product for the vendor.
    GET: Display the product creation form.
    POST: Process form submission and create product with SKU variant.
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            base_price = request.form.get('base_price')
            image_url = request.form.get('image_url')
            
            color = request.form.get('color')
            size = request.form.get('size')
            inventory = request.form.get('inventory')
            price_adjustment = request.form.get('price_adjustment', 0)
            
            if not all([name, category, base_price, color, size, inventory]):
                flash('All required fields must be filled.', 'danger')
                return render_template('vendor/product_form.html', product=None)
            
            product = ProductController.create_product(
                vendor=current_user,
                name=name,
                description=description or '',
                category=category,
                base_price=float(base_price),
                available=True,
                image_url=image_url
            )
            
            ProductController.add_sku(
                product=product,
                size=size,
                color=color,
                inventory=int(inventory),
                price_adjustment=float(price_adjustment)
            )
            
            flash('Product created successfully!', 'success')
            return redirect(url_for('vendor.dashboard'))
            
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('vendor/product_form.html', product=None)
    
    return render_template('vendor/product_form.html', product=None)


@vendor_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def edit_product(product_id):
    """
    Edit an existing product.
    GET: Display the product edit form with current values.
    POST: Process form submission and update product.
    """
    product = Product.query.get_or_404(product_id)
    
    if product.vendor_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('vendor.dashboard'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            category = request.form.get('category')
            base_price = request.form.get('base_price')
            available = request.form.get('available') == 'on'
            image_url = request.form.get('image_url')
            
            ProductController.update_product(
                product_id=product_id,
                name=name,
                description=description,
                category=category,
                base_price=float(base_price),
                available=available,
                image_url=image_url
            )
            
            flash('Product updated successfully!', 'success')
            return redirect(url_for('vendor.dashboard'))
            
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('vendor/product_form.html', product=product)
    
    return render_template('vendor/product_form.html', product=product)


@vendor_bp.route('/products/<product_id>/delete', methods=['POST'])
@login_required
@role_required('vendor')
def delete_product(product_id):
    """
    Delete a product owned by the vendor.
    Removes the product and all associated SKU variants.
    """
    try:
        product = Product.query.get_or_404(product_id)
        
        if product.vendor_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('vendor.dashboard'))
        
        success = ProductController.delete_product(product_id)
        
        if success:
            flash('Product deleted.', 'info')
        else:
            flash('Failed to delete product.', 'danger')
            
    except Exception as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('vendor.dashboard'))
