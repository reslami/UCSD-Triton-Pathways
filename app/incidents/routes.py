import os
from flask import render_template, flash, redirect, url_for, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.incidents import bp
from app.incidents.forms import IncidentReportForm, UCSD_BOUNDS
from app.models import Incident
from datetime import datetime

def save_photo(photo):
    if not photo:
        return None
    filename = secure_filename(photo.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
    return unique_filename

def is_within_ucsd_campus(lat, lng):
    """Check if coordinates are within UCSD campus boundaries"""
    return (UCSD_BOUNDS['south'] <= lat <= UCSD_BOUNDS['north'] and 
            UCSD_BOUNDS['west'] <= lng <= UCSD_BOUNDS['east'])

@bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = IncidentReportForm()
    if form.validate_on_submit():
        # Double-check coordinates are within UCSD campus (server-side validation)
        if not is_within_ucsd_campus(form.latitude.data, form.longitude.data):
            flash('Error: Location must be within UCSD campus boundaries.', 'danger')
            return render_template('incidents/report.html', title='Report Incident', form=form)
        
        photo_path = None
        if form.photo.data:
            photo_path = save_photo(form.photo.data)
        
        # Generate a more descriptive title based on incident type and vehicle type
        incident_type_display = dict(form.incident_type.choices).get(form.incident_type.data)
        vehicle_type_display = dict(form.vehicle_type.choices).get(form.vehicle_type.data)
        title = f"{incident_type_display} ({vehicle_type_display})"
        
        incident = Incident(
            title=title,
            description=form.description.data or "No description provided",
            date=form.date.data,
            location=form.location.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            incident_type=form.incident_type.data,
            weather=form.weather.data,
            vehicle_type=form.vehicle_type.data,
            severity="medium",  # Default severity for backward compatibility
            photo_path=photo_path,
            reporter=current_user
        )
        
        db.session.add(incident)
        db.session.commit()
        flash('Your incident report has been submitted!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('incidents/report.html', title='Report Incident', form=form)

@bp.route('/incident/<int:id>')
@login_required
def view_incident(id):
    incident = Incident.query.get_or_404(id)
    return render_template('incidents/view.html', title='View Incident', incident=incident) 