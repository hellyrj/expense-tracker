import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import db
from app.models import User, Setting
from app.utils import fetch_currencies


# Function to seed old users with the default currency
def seed_user_currencies():
    # Fetch the available currencies
    available_currencies = fetch_currencies()
    
    # If available currencies are empty, use default 'USD'
    if not available_currencies:
        available_currencies = ['USD']
    
    # Iterate over all users and create a Setting if it doesn't exist
    users = User.query.all()
    
    for user in users:
        # Check if the user already has a setting
        user_setting = Setting.query.filter_by(user_id=user.id).first()
        
        if not user_setting:
            # Create a new Setting with a default currency (e.g., 'USD')
            new_setting = Setting(user_id=user.id, currency='USD')
            db.session.add(new_setting)
    
    # Commit changes to the database
    db.session.commit()

# Call this function to seed the data
seed_user_currencies()
