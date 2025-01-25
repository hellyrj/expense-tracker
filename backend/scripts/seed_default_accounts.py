import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import create_app, db
from app.models import User, Account

# Create the Flask app context
app = create_app() 

with app.app_context(): 
    def seed_default_accounts():
        users = User.query.all()
        for user in users:
            Account.create_default_accounts(user.id)
        print("Default accounts seeded for all users.")

    if __name__ == "__main__":
        seed_default_accounts()
