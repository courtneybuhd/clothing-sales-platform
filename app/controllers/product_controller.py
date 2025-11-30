"""
File: app/controllers/product_controller.py
Description: Product and SKU management controller for the Multi-Brand Clothing Sales Platform.
             Provides create, read, update, delete operations for products and SKU variants.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from datetime import datetime
from app import db
from app.models.user import Vendor
from app.models.product import Product, SKU


class ProductController:
    """
    Controller class for product catalog and SKU management operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def create_product(vendor, name, description, category, base_price, available=True, image_url=None):
        """
        Create a new product for a vendor.
        
        Args:
            vendor (Vendor): Vendor who owns this product
            name (str): Product name
            description (str): Product description
            category (str): Product category
            base_price (Decimal): Base price for the product
            available (bool): Whether product is available for purchase
            image_url (str, optional): URL to product image
            
        Returns:
            Product: The newly created product
        """
        product = Product(
            vendor_id=vendor.id,
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            available=available,
            image_url=image_url
        )
        
        try:
            db.session.add(product)
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create product: {str(e)}")
    
    @staticmethod
    def update_product(product_id, **fields):
        """
        Update an existing product's fields.
        
        Args:
            product_id (str): UUID of the product to update
            **fields: Keyword arguments for fields to update
                     (name, description, category, base_price, available, image_url)
            
        Returns:
            Product: Updated product object, or None if not found
        """
        product = Product.query.get(product_id)
        
        if not product:
            return None
        
        # Allowed fields for update
        allowed_fields = ['name', 'description', 'category', 'base_price', 'available', 'image_url']
        
        # Update only allowed fields
        for field, value in fields.items():
            if field in allowed_fields and value is not None:
                setattr(product, field, value)
        
        # Update the timestamp
        product.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update product: {str(e)}")
    
    @staticmethod
    def delete_product(product_id):
        """
        Delete a product and all its SKU variants.
        
        Args:
            product_id (str): UUID of the product to delete
            
        Returns:
            bool: True if deletion succeeded, False if product not found
        """
        product = Product.query.get(product_id)
        
        if not product:
            return False
        
        try:
            # Cascade delete will handle SKUs and related records
            db.session.delete(product)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete product: {str(e)}")
    
    @staticmethod
    def add_sku(product, size, color, inventory, price_adjustment=0):
        """
        Add a new SKU variant to a product.
        
        Args:
            product (Product): Product to add SKU to
            size (str): Size variant (e.g., "S", "M", "L", "XL")
            color (str): Color variant
            inventory (int): Initial inventory count
            price_adjustment (Decimal): Price adjustment from base price
            
        Returns:
            SKU: The newly created SKU
        """
        sku = SKU(
            product_id=product.id,
            size=size,
            color=color,
            inventory=inventory,
            price_adjustment=price_adjustment
        )
        
        try:
            db.session.add(sku)
            # Update product's updated_at timestamp
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return sku
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add SKU: {str(e)}")
    
    @staticmethod
    def update_sku(sku_id, **fields):
        """
        Update an existing SKU variant.
        
        Args:
            sku_id (str): UUID of the SKU to update
            **fields: Keyword arguments for fields to update
                     (size, color, inventory, price_adjustment)
            
        Returns:
            SKU: Updated SKU object, or None if not found
        """
        sku = SKU.query.get(sku_id)
        
        if not sku:
            return None
        
        # Allowed fields for update
        allowed_fields = ['size', 'color', 'inventory', 'price_adjustment']
        
        # Update only allowed fields
        for field, value in fields.items():
            if field in allowed_fields:
                setattr(sku, field, value)
        
        # Update parent product's timestamp
        if sku.product:
            sku.product.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return sku
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update SKU: {str(e)}")
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Retrieve a product by its ID.
        
        Args:
            product_id (str): UUID of the product
            
        Returns:
            Product: Product object or None if not found
        """
        return Product.query.get(product_id)
    
    @staticmethod
    def list_products_by_category(category, only_available=True):
        """
        List all products in a specific category.
        
        Args:
            category (str): Product category to filter by
            only_available (bool): If True, return only available products
            
        Returns:
            list: List of Product objects matching criteria
        """
        query = Product.query.filter_by(category=category)
        
        if only_available:
            query = query.filter_by(available=True)
        
        return query.all()
    
    @staticmethod
    def list_vendor_products(vendor, only_available=False):
        """
        List all products belonging to a specific vendor.
        
        Args:
            vendor (Vendor): Vendor whose products to list
            only_available (bool): If True, return only available products
            
        Returns:
            list: List of Product objects owned by the vendor
        """
        query = Product.query.filter_by(vendor_id=vendor.id)
        
        if only_available:
            query = query.filter_by(available=True)
        
        return query.order_by(Product.created_at.desc()).all()
    
    @staticmethod
    def list_all_available_products():
        """
        List all products that are available and have at least one SKU with inventory.
        This is used for the customer catalog to show all browsable products across vendors.
        
        Returns:
            list: List of available Product objects that have inventory
        """
        # Get all products marked as available
        available_products = Product.query.filter_by(available=True).all()
        
        # Filter to only include products with at least one SKU that has inventory > 0
        products_with_inventory = []
        for product in available_products:
            # Check if product has any SKU with inventory
            has_inventory = any(sku.inventory > 0 for sku in product.skus)
            if has_inventory:
                products_with_inventory.append(product)
        
        return products_with_inventory
