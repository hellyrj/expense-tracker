from flask import Blueprint, flash, redirect, request, jsonify, render_template, url_for
from app import db
from app.models import Category
from flask_login import login_required, current_user

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
@login_required
def categories_page():
    # Fetch categories only once
    income_categories = Category.query.filter_by(user_id=current_user.id, type='Income').distinct().all()
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='Expense').distinct().all()

    # Pass the distinct categories to the template
    return render_template(
        'categories.html',
        income_categories=income_categories,
        expense_categories=expense_categories
    )


# Route for the categories page
@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    # Fetch all categories for the logged-in user, categorized by type (Income/Expense)
    income_categories = Category.query.filter_by(user_id=current_user.id, type='Income').all()
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='Expense').all()

    # Pass the categories to the template
    return render_template('categories.html', income_categories=income_categories, expense_categories=expense_categories)



# Route to add a new category
@categories_bp.route('/categories', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    type = request.form.get('type')

    if type not in ['Income', 'Expense']:
        
         flash('Invalid category type', 'error')
         return redirect(url_for('categories.categories_page'))

    if not name:
        flash('Category name is required', 'error')
        return redirect(url_for('categories.categories_page'))

    # Create and save the new category
    new_category = Category(user_id=current_user.id, name=name, type=type)
    db.session.add(new_category)
    db.session.commit()

    flash(f'{type} category "{name}" added successfully!', 'success')
    return redirect(url_for('categories.categories_page'))


@categories_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('categories.categories_page'))

    if request.method == 'POST':
        category.name = request.form.get('name')
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories.categories_page'))

    return render_template('edit_category.html', category=category)

@categories_bp.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('categories.categories_page'))

    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories.categories_page'))
