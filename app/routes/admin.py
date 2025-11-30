"""
File: app/routes/admin.py
Description: Admin dashboard routes for the Multi-Brand Clothing Sales Platform.
             Handles user management, vendor approval/rejection, and platform oversight.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.utils.decorators import role_required
from app.controllers.admin_controller import AdminController


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@role_required('admin')
def dashboard():
    """
    Admin dashboard displaying all users and pending vendor applications.
    Provides tools for user management and vendor approval.
    """
    users = AdminController.list_all_users()
    pending_vendors = AdminController.list_vendors(pending_only=True)
    
    return render_template('admin/dashboard.html', users=users, pending_vendors=pending_vendors)


@admin_bp.route('/vendors/<vendor_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_vendor(vendor_id):
    """
    Approve a pending vendor application.
    Sets vendor.approved to True and allows them to list products.
    """
    try:
        vendor = AdminController.approve_vendor(vendor_id)
        
        if vendor:
            flash(f'Vendor "{vendor.business_name or vendor.name}" approved successfully!', 'success')
        else:
            flash('Vendor not found.', 'danger')
            
    except Exception as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/vendors/<vendor_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_vendor(vendor_id):
    """
    Reject a pending vendor application.
    Optionally provides a reason for rejection.
    """
    try:
        reason = request.form.get('reason', 'Application does not meet requirements')
        
        # For rejection, we simply delete the vendor account
        # This matches the VendorOnboardingController.reject pattern
        vendor = AdminController.get_vendor_by_id(vendor_id)
        
        if vendor:
            # Note: In a real implementation, you might want to send an email
            # with the rejection reason before deleting
            from app import db
            db.session.delete(vendor)
            db.session.commit()
            flash(f'Vendor application rejected. Reason: {reason}', 'info')
        else:
            flash('Vendor not found.', 'danger')
            
    except Exception as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/suspend', methods=['POST'])
@login_required
@role_required('admin')
def suspend_user(user_id):
    """
    Suspend a user account, preventing login and platform access.
    """
    try:
        user = AdminController.suspend_user(user_id)
        
        if user:
            flash(f'User "{user.name}" suspended.', 'warning')
        else:
            flash('User not found.', 'danger')
            
    except Exception as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/reactivate', methods=['POST'])
@login_required
@role_required('admin')
def reactivate_user(user_id):
    """
    Reactivate a suspended user account, restoring access.
    """
    try:
        user = AdminController.unsuspend_user(user_id)
        
        if user:
            flash(f'User "{user.name}" reactivated.', 'success')
        else:
            flash('User not found.', 'danger')
            
    except Exception as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.dashboard'))
