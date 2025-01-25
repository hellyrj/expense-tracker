from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from .models import Budget, Category 

# Create a blueprint for budget-related routes
budgets_bp = Blueprint('budgets', __name__)

# Route to display all budgets for the logged-in user
@budgets_bp.route('/budgets', methods=['GET'])
@login_required   
def get_budgets():
    # Fetch budgets for the current user
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template('budgets.html', budgets=budgets)

from app import db

@budgets_bp.route('/add', methods=['GET', 'POST'])
@login_required  
def add_budget():
    try:
        # Fetch user-specific expense categories
        expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()

        # If no categories, create defaults
        if not expense_categories:
            Category.create_default_categories(current_user.id)
            expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()

        if request.method == 'POST':
            category_id = int(request.form.get('category_id'))
            amount = float(request.form.get('amount', 0.0))

            # Create a new budget linked to an expense category
            new_budget = Budget(
                user_id=current_user.id,
                amount=amount,
                category_id=category_id
            )

            db.session.add(new_budget)
            db.session.commit()
            flash('Budget added successfully!', 'success')
            return redirect(url_for('budgets.get_budgets'))

        return render_template(
            'add_budget.html',
            expense_categories=expense_categories
        )
    except Exception as e:
        flash(f"Error adding budget: {str(e)}", 'danger')
        return redirect(url_for('budgets.get_budgets'))




# Route to update a budget's amount
@budgets_bp.route('/budgets/<int:budget_id>', methods=['POST'])
@login_required
def update_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)

    # Ensure the current user owns this budget
    if budget.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to update this budget'}), 403

    new_amount = request.form.get('amount')

    if not new_amount:
        return jsonify({'error': 'Amount is required'}), 400

    # Update the budget's amount
    budget.update_amount(float(new_amount))
    return redirect(url_for('budgets.get_budgets'))

# Route to delete a budget
@budgets_bp.route('/budgets/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)

    # Ensure the current user owns this budget
    if budget.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to delete this budget'}), 403

    db.session.delete(budget)
    db.session.commit()
    return redirect(url_for('budgets.get_budgets'))
