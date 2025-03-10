from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, Optional

# UCSD campus approximate bounding box
UCSD_BOUNDS = {
    'north': 32.8920,  # North boundary latitude
    'south': 32.8680,  # South boundary latitude
    'east': -117.2100, # East boundary longitude (extended to include medical center)
    'west': -117.2480  # West boundary longitude
}

def validate_coordinates(form, field):
    # This validator will be used for both latitude and longitude fields
    # We'll check the complete coordinates only when validating longitude
    if field.name == 'longitude':
        lat = form.latitude.data
        lng = form.longitude.data
        
        if lat is None or lng is None:
            raise ValidationError('Coordinates are required. Please click on the map to set a location.')
            
        # Check if coordinates are within UCSD campus boundaries
        if not (UCSD_BOUNDS['south'] <= lat <= UCSD_BOUNDS['north'] and 
                UCSD_BOUNDS['west'] <= lng <= UCSD_BOUNDS['east']):
            raise ValidationError('Location must be within UCSD campus boundaries.')

class IncidentReportForm(FlaskForm):
    # Location fields
    latitude = FloatField('Latitude', validators=[DataRequired(), validate_coordinates])
    longitude = FloatField('Longitude', validators=[DataRequired(), validate_coordinates])
    location = StringField('📍 Location Description', validators=[DataRequired()])
    
    # Date and time
    date = DateTimeLocalField('🕒 Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    
    # Incident details
    incident_type = SelectField('⚠️ Incident Type', 
        choices=[
            ('collision_vehicle', 'Collision with Vehicle'),
            ('collision_pedestrian', 'Collision with Pedestrian'),
            ('single_vehicle_fall', 'Single-Vehicle Fall'),
            ('flat_tire_puncture', 'Flat Tire/Puncture'),
            ('obstruction_hazard', 'Obstruction/Hazard on Path'),
            ('weather_related', 'Weather-Related Incident'),
            ('hit_and_run', 'Hit and Run'),
            ('mechanical_issue', 'Mechanical Issue'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    
    # Vehicle type
    vehicle_type = SelectField('🛴 Vehicle Type', 
        choices=[
            ('scooter', 'Scooter'),
            ('bike', 'Bike'),
            ('skateboard', 'Skateboard'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    
    # Weather condition
    weather = SelectField('🌦️ Weather', 
        choices=[
            ('clear', 'Clear'),
            ('rainy', 'Rainy'),
            ('foggy', 'Foggy'),
            ('windy', 'Windy'),
            ('other', 'Other')
        ],
        validators=[DataRequired()]
    )
    
    # Description - now optional
    description = TextAreaField('📄 Brief Description', validators=[Optional()])
    
    # Photo - still optional
    photo = FileField('📷 Add Photo (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    # Submit button
    submit = SubmitField('Submit Report') 