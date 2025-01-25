from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Account

account_bp = Blueprint('account', __name__, url_prefix='/account')

@account_bp.route('/list', methods=['GET'])
@login_required
def list_accounts():
    """
    Display all accounts for the logged-in user.
    """
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('list_accounts.html', accounts=user_accounts)

@account_bp.route('/add', methods=['POST'])
@login_required
def add_account():
    """z
    Add a new account for the logged-in user.
    """
    account_type = request.form.get('account_type')
    initial_balance = request.form.get('balance', 0.0, type=float)

    if not account_type:
        flash("Account type is required!", "warning")
        return redirect(url_for('account.list_accounts'))

    # Check for duplicate account type
    existing_account = Account.query.filter_by(user_id=current_user.id, account_type=account_type).first()
    if existing_account:
        flash(f"An account with type '{account_type}' already exists.", "warning")
        return redirect(url_for('account.list_accounts'))

    # Add new account
    new_account = Account(
        user_id=current_user.id,
        account_type=account_type,
        balance=initial_balance
    )
    db.session.add(new_account)
    db.session.commit()

    flash(f"Account '{account_type}' added successfully!", "success")
    return redirect(url_for('account.list_accounts'))

@account_bp.route('/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """
    Edit an existing account.
    """
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        flash("Account not found or unauthorized access.", "danger")
        return redirect(url_for('account.list_accounts'))

    if request.method == 'POST':
        account_type = request.form.get('account_type')
        balance = request.form.get('balance', type=float)

        if not account_type:
            flash("Account type is required!", "warning")
            return redirect(url_for('account.edit_account', account_id=account_id))

        account.account_type = account_type
        account.balance = balance
        db.session.commit()

        flash(f"Account '{account_type}' updated successfully!", "success")
        return redirect(url_for('account.list_accounts'))

    return render_template('edit_account.html', account=account)


@account_bp.route('/delete/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    """
    Delete an account.
    """
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        flash("Account not found or unauthorized access.", "danger")
        return redirect(url_for('account.list_accounts'))

    db.session.delete(account)
    db.session.commit()

    flash(f"Account '{account.account_type}' deleted successfully!", "success")
    return redirect(url_for('account.list_accounts'))
