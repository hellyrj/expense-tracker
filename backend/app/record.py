    #The Record class should handle:

    #Storing individual expense/income records.
    #Tracking details such as amount, description, category, date, and user association.
    #Supporting CRUD (Create, Read, Update, Delete) operations if required.
from datetime import date, datetime, timedelta  
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Account, Analysis, Category, db, Record

record_bp = Blueprint('record', __name__, url_prefix='/record')

@record_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    try:
        # Fetch user-specific accounts and categories
        accounts = Account.query.filter_by(user_id=current_user.id).all()
        income_categories = Category.query.filter_by(user_id=current_user.id, type='income').all()
        expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()

        if request.method == 'POST':
            record_id = request.form.get('record_id')
            record_type = request.form.get('type')  # 'income' or 'expense'
            account_id = int(request.form.get('account_id'))
            category_id = int(request.form.get('category_id'))
            amount = float(request.form.get('amount', 0.0))
            description = request.form.get('description', '')
            date_range = request.form.get('date_range', datetime.now().strftime('%Y-%m-%d'))

            if record_id:  # Update existing record
                record = Record.query.filter_by(id=record_id, username=current_user.username).first()
                if not record:
                    flash("Record not found!", 'danger')
                    return redirect(url_for('record.add_record'))

                # Handle type change (income <-> expense)
                if record_type == 'income':
                    record.total_expense = 0.0  # Clear expense value
                    record.total_income = amount
                elif record_type == 'expense':
                    record.total_income = 0.0  # Clear income value
                    record.total_expense = amount
                
                # Update other fields
                record.category_id = category_id
                record.account_id = account_id
                record.description = description
                record.date_range = date_range
                
               
                
                  # Validate the record
                try:
                    Record.validate_record(record)
                    db.session.commit()
                    flash('Record updated successfully!', 'success')
                except ValueError as e:
                    flash(str(e), 'danger')
                    return redirect(url_for('record.add_record'))
                
                return redirect(url_for('record.get_records'))
            else:
                # Create a new record
                new_record = Record(
                    username=current_user.username,
                    account_id=account_id,
                    category_id=category_id,
                    total_income=amount if record_type == 'income' else 0.0,
                    total_expense=amount if record_type == 'expense' else 0.0,
                    description=description,
                    date_range=date_range,
                )
                db.session.add(new_record)
                db.session.commit()
                flash('Record added successfully!', 'success')
                return redirect(url_for('record.get_records'))

        # Handle GET request for prepopulating record data
        record_id = request.args.get('record_id')
        record = None
        if record_id:
            record = Record.query.filter_by(id=record_id, username=current_user.username).first()

        return render_template(
            'add_record.html',
            accounts=accounts,
            income_categories=income_categories,
            expense_categories=expense_categories,
            record=record,
            datetime = datetime
        )
    except Exception as e:
        flash(f"Error adding record: {str(e)}", 'danger')
        return redirect(url_for('record.get_records'))




@record_bp.route('/update/<int:record_id>', methods=['GET', 'POST'])
@login_required
def update_record(record_id):
    try:
        record = Record.query.filter_by(id=record_id, username=current_user.username).first()
        if not record:
            flash("Record not found!", 'danger')
            return redirect(url_for('record.get_records'))

        # Redirect to add_record form with existing data
        return redirect(url_for('record.add_record', record_id=record_id))
    except Exception as e:
        flash(f"Error updating record: {str(e)}", 'danger')
        return redirect(url_for('record.get_records'))






@record_bp.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    try:
        # Fetch the record by ID
        record = Record.query.get(record_id)
        
        # Check if the record exists
        if not record:
            flash("Record not found.", "warning")
            return redirect(url_for('record.get_records'))
        
        # Ensure the current user is authorized to delete the record
        if record.username != current_user.username:
            flash("You are not authorized to delete this record.", "danger")
            return redirect(url_for('record.get_records'))
        
        # Delete the record
        db.session.delete(record)
        db.session.commit()
        
        flash("Record deleted successfully!", "success")
        return redirect(url_for('record.get_records'))
    
    except Exception as e:
        flash(f"Error deleting record: {str(e)}", "danger")
        return redirect(url_for('record.get_records'))


@record_bp.route('/summary', methods=['GET'])
@login_required
def get_record_summary():
    try:
        username = current_user.username  # Use current logged-in user's username

        # Retrieve the summary for the user
        summary = Record.get_summary_by_user(username)

        # If no summary is found, you can provide a default message
        if not summary:
            flash("No summary available for this user.", "warning")
            return redirect(url_for('dashboard_routes.dashboard'))

        return render_template('record_summary.html', summary=summary)

    except Exception as e:
        flash(f"Error retrieving record summary: {str(e)}", 'danger')
        return redirect(url_for('dashboard_routes.dashboard'))




# Get a specific record (GET)
@record_bp.route('/view', methods=['GET'])
@login_required
def get_records():
     
    try:
        # Fetch the user's records with account and category data
        records = Record.query.options(
            joinedload(Record.account),   # Load the related account
            joinedload(Record.category)    # Load the related category
        ).filter_by(username=current_user.username).all()

        return render_template('record_detail.html', records=records)

    except Exception as e:
        flash(f"Error fetching records: {str(e)}", 'danger')
        return redirect(url_for('dashboard_routes.dashboard'))

@record_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """
    Fetch income and expense data and generate an overview graph for daily, weekly, and monthly intervals.
    """
    try:
        # Parse the date range from the request (or use defaults)
        start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))

        # Fetch and aggregate income and expense data
        data = Analysis.get_income_expense_by_date_range(current_user.id, start_date, end_date)

        # Generate charts for different intervals
        analysis = Analysis(user_id=current_user.id, income_data=data['income'], expense_data=data['expenses'])
        daily_data = analysis.generate_chart('daily')
        weekly_data = analysis.generate_chart('weekly')
        monthly_data = analysis.generate_chart('monthly')

        return render_template(
            'overview.html',
            daily_data=daily_data,
            weekly_data=weekly_data,
            monthly_data=monthly_data,
        )
    except Exception as e:
        flash(f"Error fetching overview: {str(e)}", 'danger')
        return redirect(url_for('dashboard_routes.dashboard'))
