import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Category, User

# Create the Flask app context
app = create_app()

with app.app_context():
    def seed_default_categories():
        users = User.query.all()  # Get all users
        income_categories = ['Awards', 'Coupons', 'Grants', 'Lottery', 'Refunds', 'Rental', 'Salary', 'Sale']
        expense_categories = ['Beauty', 'Baby', 'Car Bills', 'Clothing', 'Education', 'Electronics', 'Health', 'Food', 'Entertainment', 'Home', 'Shopping', 'Social', 'Sport', 'Tax', 'Telephone', 'Transportation']

        for user in users:
            # Seed income categories
            for name in income_categories:
                category = Category(user_id=user.id, name=name, type='Income')
                db.session.add(category)

            # Seed expense categories
            for name in expense_categories:
                category = Category(user_id=user.id, name=name, type='Expense')
                db.session.add(category)

        db.session.commit()
        print("Default categories seeded for all users.")

    # Seed default categories when script runs
    if __name__ == "__main__":
        seed_default_categories()
