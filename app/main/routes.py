from flask import render_template, jsonify, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from app.main import bp
from app.models import Incident, User
from app import db
from datetime import datetime
import io
import csv
from werkzeug.utils import secure_filename

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    user_incidents = current_user.incidents.order_by(Incident.timestamp.desc()).all()
    all_incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    return render_template('main/dashboard.html', title='Dashboard', 
                         incidents=user_incidents if current_user.role != 'Admin' else all_incidents,
                         all_incidents=all_incidents)

@bp.route('/api/incidents')
@login_required
def get_incidents():
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    return jsonify([incident.to_dict() for incident in incidents])

@bp.route('/delete_all_incidents', methods=['POST'])
@login_required
def delete_all_incidents():
    try:
        Incident.query.delete()
        db.session.commit()
        flash('All incidents have been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting incidents.', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/delete_incident/<int:id>', methods=['POST'])
@login_required
def delete_incident(id):
    try:
        incident = Incident.query.get_or_404(id)
        db.session.delete(incident)
        db.session.commit()
        flash('Incident has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the incident.', 'danger')
    return redirect(url_for('main.dashboard'))

@bp.route('/export_incidents')
@login_required
def export_incidents():
    # Check if user is admin
    if current_user.role != 'Admin':
        flash('You do not have permission to export data.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get all incidents
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    
    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID', 'Title', 'Date', 'Time', 'Location', 'Latitude', 'Longitude',
        'Description', 'Incident Type', 'Vehicle Type', 'Weather', 'Severity', 
        'Reporter Username', 'Reporter Email', 'Reported On Date (UTC)', 'Reported On Time (UTC)'
    ])
    
    # Write data rows
    for incident in incidents:
        reporter_username = 'Anonymous'
        reporter_email = 'N/A'
        
        if incident.reporter:
            reporter_username = incident.reporter.username
            reporter_email = incident.reporter.email
            
        writer.writerow([
            incident.id,
            incident.title,
            incident.date.strftime('%Y-%m-%d'),  # Date only
            incident.date.strftime('%H:%M'),     # Time only
            incident.location,
            incident.latitude,
            incident.longitude,
            incident.description,
            incident.incident_type,
            incident.vehicle_type or 'N/A',      # Vehicle type (with fallback)
            incident.weather or 'N/A',           # Weather (with fallback)
            incident.severity,
            reporter_username,
            reporter_email,
            incident.timestamp.strftime('%Y-%m-%d'),  # Reported date
            incident.timestamp.strftime('%H:%M')      # Reported time
        ])
    
    # Prepare response
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=incidents_export_{timestamp}.csv"}
    )

@bp.route('/import_incidents', methods=['GET', 'POST'])
@login_required
def import_incidents():
    # Check if user is admin
    if current_user.role != 'Admin':
        flash('You do not have permission to import data.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if not file.filename.endswith('.csv'):
            flash('Only CSV files are allowed.', 'danger')
            return redirect(request.url)
        
        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            skipped_count = 0
            
            for row in csv_reader:
                try:
                    # Check if incident with same details already exists
                    existing = Incident.query.filter_by(
                        date=datetime.strptime(f"{row['Date']} {row['Time']}", '%Y-%m-%d %H:%M'),
                        location=row['Location'],
                        incident_type=row['Incident Type']
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Find reporter if username exists
                    reporter = None
                    if row['Reporter Username'] != 'Anonymous':
                        reporter = User.query.filter_by(username=row['Reporter Username']).first()
                    
                    # Create new incident
                    incident = Incident(
                        title=row['Title'],
                        description=row['Description'],
                        date=datetime.strptime(f"{row['Date']} {row['Time']}", '%Y-%m-%d %H:%M'),
                        location=row['Location'],
                        latitude=float(row['Latitude']),
                        longitude=float(row['Longitude']),
                        incident_type=row['Incident Type'],
                        vehicle_type=row['Vehicle Type'] if row['Vehicle Type'] != 'N/A' else None,
                        weather=row['Weather'] if row['Weather'] != 'N/A' else None,
                        severity=row['Severity'],
                        reporter=reporter or current_user,  # Default to current user if no match
                        timestamp=datetime.strptime(
                            f"{row['Reported On Date (UTC)']} {row['Reported On Time (UTC)']}", 
                            '%Y-%m-%d %H:%M'
                        ) if 'Reported On Date (UTC)' in row else datetime.utcnow()
                    )
                    
                    db.session.add(incident)
                    imported_count += 1
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error importing row: {str(e)}', 'danger')
                    return redirect(request.url)
            
            db.session.commit()
            flash(f'Successfully imported {imported_count} incidents. Skipped {skipped_count} duplicates.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('main/import.html', title='Import Incidents') 