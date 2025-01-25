# app/routes.py

from flask import Blueprint, jsonify , session,render_template , redirect , url_for , request , flash
from flask_login import login_user, logout_user
from flask_login import login_required , current_user

from app.utils import fetch_currencies
from .models import Account, Category, Setting, db, User

#dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

bp = Blueprint('auth' , __name__, url_prefix='/auth')
main = Blueprint('main', __name__)

@main.route('/')
def index():
     return "<p>test one </p>"


@bp.route('/register', methods=['GET', 'POST'])# those methods are built-in http request methods that are part of the http protocol

#GET -> used to request data from the server
# POST -> used to submit data to the server 
def register():
    if request.method == 'POST':
        # request is a global object in Flask that holds the data of the current request.
        #The request object in Flask provides access to all parts of the incoming HTTP request
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        currency = request.form['currency']
        # The request object in Flask provides access to all parts of the incoming HTTP request

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        # Create a new user and set the password hash
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


        # Create default accounts for the user
        default_account_types = ['Cash', 'Card (Visa)', 'Savings']
        for account_type in default_account_types:
            default_account = Account(
                user_id= user.id,
                account_type=account_type,
                balance=0.0
            )
            db.session.add(default_account)
        db.session.commit()

        # Create default settings for the user
        default_setting = Setting(user_id=user.id, currency=currency)
        db.session.add(default_setting)


        
        # Create default income and expense categories for the new user
        income_categories = ['Awards', 'Coupons', 'Grants', 'Lottery', 'Refunds', 'Rental', 'Salary', 'Sale']
        expense_categories = ['Beauty', 'Baby', 'Car Bills', 'Clothing', 'Education', 'Electronics', 'Health', 'Food', 'Entertainment', 'Home', 'Shopping', 'Social', 'Sport', 'Tax', 'Telephone', 'Transportation']

        for name in income_categories:
            income_category = Category(user_id=user.id, name=name, type='Income')
            db.session.add(income_category)

        for name in expense_categories:
            expense_category = Category(user_id=user.id, name=name, type='Expense')
            db.session.add(expense_category)

        # Commit the transaction to save the user and categories
        db.session.commit()
        flash('Account created successfully', 'success')
         # Fetch currencies dynamically using an API
       # currency = fetch_currencies()  # Fetch list of currencies
       # return render_template('register.html', currency=currency)
        return redirect(url_for('auth.login'))
  
    # Define currency for the GET request (could be a default or fetched dynamically)
   # currency = "USD"  # Set a default currency if necessary
   # return render_template('register.html', currency=currency)
    currencies = fetch_currencies()  # Replace with a list if `fetch_currencies()` is not implemented
    return render_template('register.html', currencies=currencies)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard_routes.dashboard'))  # Change 'dashboard' to your actual route
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@bp.route('/logout') 
def logout():
    logout_user()
    session.clear
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@login_required
@bp.route('/profile', methods=['GET', 'POST'])
def profile():
   
    return render_template('profile.html' , user= current_user)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_setting = Setting.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        new_currency = request.form['currency']
        user_setting.currency = new_currency
        db.session.commit()
        flash('Currency updated successfully', 'success')
        return redirect(url_for('auth.settings'))

    # Fetch currencies dynamically
    currency_list = fetch_currencies()
    return render_template('settings.html', currency_list=currency_list, current_currency=user_setting.currency)
