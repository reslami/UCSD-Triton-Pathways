# Triton Pathways

A web platform for tracking and managing micromobility incidents on the UCSD campus. This application helps identify safety trends and areas needing attention to improve campus mobility safety.

## Features

- Interactive incident reporting with map location selection
- Real-time incident visualization through markers and heatmaps
- Comprehensive incident tracking with detailed information
- Photo upload capability for better documentation
- CSV import/export functionality for data management
- Dark mode support for comfortable viewing
- Mobile-responsive design

## Tech Stack

- Python 3.13
- Flask (Web Framework)
- SQLite (Database)
- SQLAlchemy (Database ORM)
- Bootstrap 5 (Frontend Framework)
- Leaflet.js (Interactive Maps)

## Local Development Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///app.db
   UPLOAD_FOLDER=app/static/uploads
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   flask db upgrade
   ```

5. Run the development server:
   ```bash
   python run.py
   ```
   The application will be available at http://localhost:5000

## Testing

Run tests with pytest:
```bash
pytest
```

For test coverage report:
```bash
coverage run -m pytest
coverage report
coverage html  # For detailed HTML report
```

## Code Quality

Maintain code quality by running:
```bash
black .  # Format code
flake8    # Lint code
```

## Database Management

The application uses SQLite for data storage. The database file is located at `instance/app.db`.

To reset the database:
1. Delete the `instance/app.db` file
2. Run `python init_db.py`
3. Run `flask db upgrade`

## Default Admin Account

After initializing the database, you can log in with:
- Email: admin@example.com
- Password: change-this-password-immediately

**IMPORTANT**: Change the admin password immediately after first login.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). See the [LICENSE](LICENSE) file for details or visit [Creative Commons](http://creativecommons.org/licenses/by-nc-sa/4.0/) for more information.

## Acknowledgments

- UCSD Transportation Services for inspiration
- OpenStreetMap for map data
- Bootstrap Icons for the icon set 