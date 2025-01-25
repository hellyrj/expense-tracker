from flask import request, jsonify
from app import db
from app.models import Analysis, Category
from datetime import datetime  
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Account, Category, db, Record


analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@analysis_bp.route('/create-analysis', methods=['POST'])
def create_analysis():
    """
    Create an analysis for the user and render the analysis results in a template.
    """
    try:
        # Get the request data (e.g., user_id and date_range)
        data = request.form
        user_id = data.get('user_id')
        date_range = data.get('date_range')  # 'daily', 'weekly', 'monthly'

        if not user_id or not date_range:
            return render_template('error.html', message="User ID and date range are required.")

        # Create the analysis using the Analysis model
        analysis = Analysis.create_analysis(user_id, date_range)

        # Pass the analysis data to the template for rendering
        return render_template(
            'analysis.html', 
            analysis=analysis,
            income_data=analysis.income_data,
            expense_data=analysis.expense_data,
            date_range=analysis.date_range
        )
    
    except Exception as e:
        # Handle any errors and render an error page
        return render_template('error.html', message=str(e))