from datetime import datetime, timezone, date
from sqlalchemy import func
from app import db , login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
#from . import db, login_manager 

bcrypt = Bcrypt() 
class User(db.Model , UserMixin):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    #settings = db.relationship('Setting', back_populates='user')
    # Check if the provided password matches the stored hash
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    # Method to set the password hash from a plain password
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')



class Record(db.Model):
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)  # Foreign Key to Account model
    username = db.Column(db.String(80), db.ForeignKey('users.username'), nullable=False)
    total_income = db.Column(db.Float, default=0.0)
    total_expense = db.Column(db.Float, default=0.0)
    date_range = db.Column(db.String(50), nullable=False)  # e.g., '2024-01', '2024-Q1'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # Foreign Key to Category model
    description = db.Column(db.String(255), nullable=True)  # Add description field

    user = db.relationship('User', backref=db.backref('records', lazy=True))
    account = db.relationship('Account', backref=db.backref('records', lazy=True))
    category = db.relationship('Category', backref=db.backref('records', lazy=True))

    @property
    def net_balance(self):
        """Calculate and return the net balance dynamically."""
        return self.total_income - self.total_expense

    def calculate_net_balance(self):
        """Recalculate and update the net balance."""
        self.net_balance = self.total_income - self.total_expense

    def add_income(self, amount):
        """Add income to the record and recalculate the net balance."""
        if amount < 0:
            raise ValueError("Income amount cannot be negative.")
        self.total_income += amount
        self.calculate_net_balance()

    def add_expense(self, amount):
        """Add an expense to the record and recalculate the net balance."""
        if amount < 0:
            raise ValueError("Expense amount cannot be negative.")
        self.total_expense += amount
        self.calculate_net_balance()

    def update_income(self, new_income):
        """Update the total income value directly and recalculate the net balance."""
        if new_income < 0:
            raise ValueError("Income amount cannot be negative.")
        self.total_income = new_income
        self.calculate_net_balance()

    def update_expense(self, new_expense):
        """Update the total expense value directly and recalculate the net balance."""
        if new_expense < 0:
            raise ValueError("Expense amount cannot be negative.")
        self.total_expense = new_expense
        self.calculate_net_balance()

    def save(self):
        """Save the record to the database."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def to_dict(self):
        """Convert the record instance to a dictionary format."""
        return {
            'id': self.id,
            'username': self.username,
            'total_income': self.total_income,
            'total_expense': self.total_expense,
            'net_balance': self.net_balance,
            'date_range': self.date_range
        }

    @staticmethod
    def get_by_user(username):
        """Retrieve a record for a specific username and date range."""
        return Record.query.filter_by(username=username)

    @staticmethod
    def get_summary_by_user(username):
        """Generate a summary for a specific user (aggregating income and expense)."""
        result = db.session.query(
            func.sum(Record.total_income).label('total_income'),
            func.sum(Record.total_expense).label('total_expense')
        ).filter_by(username=username).first()

        total_income = result.total_income if result.total_income else 0.0
        total_expense = result.total_expense if result.total_expense else 0.0
        net_balance = total_income - total_expense  # Compute net balance dynamically

        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
        }

    @staticmethod
    def validate_record(record):
        """Ensure only one of income or expense has a value."""
        if record.total_income > 0 and record.total_expense > 0:
            raise ValueError("A record cannot have both income and expense values.")

  

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_range = db.Column(db.String(50))  # e.g., '2024-01', '2024-Q1', etc.
    income_data = db.Column(db.JSON)  # Store income data for charting
    expense_data = db.Column(db.JSON)  # Store expense data for charting

    user = db.relationship('User', backref=db.backref('analyses', lazy=True))

    def generate_chart(self):
        """
        Generate a chart based on the income and expense data stored in this analysis.
        """
        income = self.income_data
        expenses = self.expense_data
        return {"income": income, "expenses": expenses}

    @staticmethod
    def create_analysis(user_id, date_range):
        """
        Create a new analysis by aggregating income and expenses data
        based on the given date range.
        """
        # Set up income and expense data containers
        income_data = {}
        expense_data = {}

        # Aggregating income and expenses by the selected date range (daily, weekly, monthly)
        if date_range == 'daily':
            # Aggregating daily income data
            income_query = db.session.query(
                Category.name,
                func.sum(Category.amount).label('total_income')
            ).filter(Category.user_id == user_id, Category.type == 'Income').group_by(Category.name).all()

            # Aggregating daily expense data
            expense_query = db.session.query(
                Category.name,
                func.sum(Category.amount).label('total_expense')
            ).filter(Category.user_id == user_id, Category.type == 'Expense').group_by(Category.name).all()

            # Store the results in the dictionaries
            income_data = {name: total_income for name, total_income in income_query}
            expense_data = {name: total_expense for name, total_expense in expense_query}

        elif date_range == 'weekly':
            # Aggregating weekly income and expense data
            income_query = db.session.query(
                func.date_trunc('week', Category.date).label('week_start'),
                func.sum(Category.amount).label('total_income')
            ).filter(Category.user_id == user_id, Category.type == 'Income').group_by(func.date_trunc('week', Category.date)).all()

            expense_query = db.session.query(
                func.date_trunc('week', Category.date).label('week_start'),
                func.sum(Category.amount).label('total_expense')
            ).filter(Category.user_id == user_id, Category.type == 'Expense').group_by(func.date_trunc('week', Category.date)).all()

            income_data = {str(week_start): total_income for week_start, total_income in income_query}
            expense_data = {str(week_start): total_expense for week_start, total_expense in expense_query}

        elif date_range == 'monthly':
            # Aggregating monthly income and expense data
            income_query = db.session.query(
                func.date_trunc('month', Category.date).label('month_start'),
                func.sum(Category.amount).label('total_income')
            ).filter(Category.user_id == user_id, Category.type == 'Income').group_by(func.date_trunc('month', Category.date)).all()

            expense_query = db.session.query(
                func.date_trunc('month', Category.date).label('month_start'),
                func.sum(Category.amount).label('total_expense')
            ).filter(Category.user_id == user_id, Category.type == 'Expense').group_by(func.date_trunc('month', Category.date)).all()

            income_data = {str(month_start): total_income for month_start, total_income in income_query}
            expense_data = {str(month_start): total_expense for month_start, total_expense in expense_query}

        # Create the analysis record
        analysis = Analysis(
            user_id=user_id,
            date_range=date_range,
            income_data=income_data,
            expense_data=expense_data
        )

        db.session.add(analysis)
        db.session.commit()
        return analysis
    

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    user = db.relationship('User', backref=db.backref('budgets', lazy=True))
    category = db.relationship('Category', backref=db.backref('budgets', lazy=True))

    def update_amount(self, new_amount):
        """
        Update the allocated amount for this budget.
        """
        self.amount = new_amount
        db.session.commit()





class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(100), nullable=False)  # e.g., 'Cash', 'Savings', 'Credit Card'
    balance = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref=db.backref('accounts', lazy=True))

    def update_balance(self, amount):
        """
        Update the balance of the account by adding/subtracting the given amount.
        """
        self.balance += amount
        db.session.commit()


    @staticmethod
    def create_default_accounts(user_id):
        """Create default accounts for a user."""
        default_accounts = ['Cash', 'Card (Visa)', 'Savings']
        for account_type in default_accounts:
            if not Account.query.filter_by(user_id=user_id, account_type=account_type).first():
                new_account = Account(
                    user_id=user_id,
                    account_type=account_type,
                    balance=0.0
                )
                db.session.add(new_account)
        db.session.commit()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., 'Salary', 'Education'
    type = db.Column(db.String(50), nullable=False)  # e.g., 'Income', 'Expense'
    amount = db.Column(db.Numeric(10,2), nullable=False, default=0)     # The amount for each income/expense
    date = db.Column(db.Date, nullable=False)        # The date of income/expense
   
    user = db.relationship('User', backref=db.backref('categories', lazy=True))

    @staticmethod
    def create_default_categories(user_id):
        default_income = ['Awards', 'Coupons', 'Grants', 'Lottery', 'Refunds', 'Rental', 'Salary', 'Sale']
        default_expense = ['Beauty', 'Baby', 'Car Bills', 'Clothing', 'Education', 'Electronics',
                           'Health', 'Food', 'Entertainment', 'Home', 'Shopping', 'Social', 
                           'Sport', 'Tax', 'Telephone', 'Transportation']

        categories = [
            Category(user_id=user_id, name=name, type='Income') for name in default_income
        ] + [
            Category(user_id=user_id, name=name, type='Expense') for name in default_expense
        ]

        db.session.bulk_save_objects(categories)
        db.session.commit()


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')

    user = db.relationship('User', backref='user_settings' , overlaps="settings")


@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))