from flask import Blueprint, render_template, redirect, url_for


# Define the routes for each model
  # Create a Blueprint for routes
dashboard_routes = Blueprint('dashboard_routes', __name__)


@dashboard_routes.route('/dashboard')
def dashboard():
    # This route will provide links to the 8 routes
    return render_template('dashboard.html')  # You can create a dashboard template
