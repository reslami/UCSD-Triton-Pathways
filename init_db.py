from app import create_app, db
from app.models import User
import sys

def init_db():
    print("Starting database initialization...")
    try:
        app = create_app()
        with app.app_context():
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Check if admin user exists
            print("Checking for admin user...")
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                print("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='Admin'
                )
                admin.set_password('change-this-password-immediately')
                db.session.add(admin)
                db.session.commit()
                print('Admin user created successfully!')
            else:
                print('Admin user already exists!')
            
            print("Database initialization completed successfully!")
            return True
    except Exception as e:
        print(f"Error during database initialization: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = init_db()
    if not success:
        sys.exit(1)  # Exit with error code if initialization failed 