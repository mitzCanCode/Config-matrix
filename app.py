### IMPORTS
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import secrets
import re
from config_mtrx_module.computers import get_computer_progress, get_computer_assigned_technician, get_computer_deadline, create_computer, create_computer_by_id
import json
from datetime import datetime

### App set up

# Creating a web application instance
app = Flask(__name__)
# Set the secret key for securely signing the session cookies and CSRF tokens
app.secret_key = secrets.token_hex(16) # Generate a secure random 32-character hex key
# Set db location for Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///computers.db"
# Making session cookies be able to only be sent over secure HTTPS connections
app.config['SESSION_COOKIE_SECURE'] = False ### SET TO TRUE IN REAL ENV
# Prevent client-side JavaScript from accessing the session cookie
app.config['SESSION_COOKIE_HTTPONLY'] = True
# Set the SameSite policy to 'Lax' to help avoid CSRF attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Ensures the session cookie is not sent with most cross-site requests, except top-level navigations
# Session configuration for better concurrent handling
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request
db = SQLAlchemy(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.session_protection = 'strong'  # Strong session protection

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    # Custom validator for password strength
    def validate_password(self, field):
        password = field.data
        if len(password) < 8 or len(password) > 12:
            raise ValidationError('Password must be between 8 and 12 characters long.')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')
        
        if not re.search(r'[!@#\$%\^\&\*]', password):
            raise ValidationError('Password must contain at least one special character: !, @, #, $, %, etc.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Import your existing technicians model and functions
from config_mtrx_module.technicians import create_technician, verify_user
from config_mtrx_module.db import session, Technicians, Computers
from flask_login import UserMixin

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Create a separate session for user loading to avoid conflicts
    from config_mtrx_module.db import Session
    user_session = Session()
    
    try:
        technician = user_session.query(Technicians).filter_by(id=int(user_id)).first()
        if technician:
            return User(technician.id, technician.name)
        return None
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None
    finally:
        user_session.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Use your existing verify_user function
        success, message, _ = verify_user(username, password) # type: ignore
        
        if success:
            # Get the technician from the database
            technician = session.query(Technicians).filter_by(name=username).first()
            if technician:
                user = User(technician.id, technician.name)
                login_user(user)
                flash('Login successful!', 'success')
                
                # Handle the next parameter safely
                next_page = request.args.get('next')
                if next_page:
                    # Validate the next URL to prevent open redirects
                    from urllib.parse import urlparse, urljoin
                    if urlparse(next_page).netloc == '':
                        # Only allow relative URLs (same domain)
                        return redirect(urljoin(request.host_url, next_page))
                
                # Default redirect to dashboard
                return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Use your existing create_technician function
        success, message, _ = create_technician(username, password) # type: ignore
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/computer_info/<computer_name>', methods=['GET'])
@login_required
def api_computer_info(computer_name):
    try:
        computer_data = computer_info(computer_name)
        if "Error" in computer_data:
            return app.response_class(
                response=json.dumps(computer_data),
                status=computer_data.get("code", 500),
                mimetype='application/json'
            )
        return app.response_class(
            response=json.dumps(computer_data),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in api_computer_info: {e}")
        return app.response_class(
            response=json.dumps({"Error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/computers', methods=['GET'])
@login_required
def api_computers():
    # Create a new session for this request
    from config_mtrx_module.db import Session
    local_session = Session()
    
    try:
        # Load all computers at once instead of using pagination
        computers = local_session.query(Computers).all()
        computer_list = [{"name": c.name} for c in computers]
        return app.response_class(
            response=json.dumps(computer_list),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in api_computers: {e}")
        return app.response_class(
            response=json.dumps({"Error": str(e)}),
            status=500,
            mimetype='application/json'
        )
    finally:
        local_session.close()
        
@app.route('/api/add_computer', methods=['POST'])
@csrf.exempt
@login_required
def add_api_computers():
    try:
        data = request.get_json()

        # Extract and validate the parameters
        name = data.get('name')
        deadline_str = data.get('deadline')
        profile_id = data.get('profile_id')
        technician_id = data.get('technician_id')

        if not all([name, deadline_str, profile_id is not None, technician_id is not None]):
            missing = []
            if not name: missing.append('name')
            if not deadline_str: missing.append('deadline')
            if profile_id is None: missing.append('profile_id')
            if technician_id is None: missing.append('technician_id')
            print(f"Missing parameters: {missing}")
            raise ValueError(f"Missing parameters: {', '.join(missing)}")

        # Convert deadline to datetime
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Deadline must be in 'YYYY-MM-DD HH:MM:SS' format.")

        # Validate profile_id and technician_id are integers
        try:
            profile_id = int(profile_id)
            technician_id = int(technician_id)
        except (ValueError, TypeError):
            raise ValueError("profile_id and technician_id must be valid integers.")

        # Call create_computer_by_id
        creation_status, message, status_code = create_computer_by_id(name=name, deadline=deadline, profile_id=profile_id, technician_id=technician_id)

        return app.response_class(
            response=json.dumps({'message': message}),
            status=status_code,
            mimetype='application/json'
        )
    except ValueError as ve:
        return app.response_class(
            response=json.dumps({'Error': str(ve)}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in add_api_computers: {e}")
        return app.response_class(
            response=json.dumps({'Error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/profiles', methods=['GET'])
@login_required
def api_profiles():
    try:
        from config_mtrx_module.profiles import retrieve_all_profiles
        success, message, profiles, status_code = retrieve_all_profiles()
        
        if success:
            profile_list = [{
                "id": profile.id,
                "name": profile.name,
                "description": getattr(profile, 'description', '')
            } for profile in profiles]
            
            return app.response_class(
                response=json.dumps(profile_list),
                status=200,
                mimetype='application/json'
            )
        else:
            return app.response_class(
                response=json.dumps({"Error": message}),
                status=status_code,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error in api_profiles: {e}")
        return app.response_class(
            response=json.dumps({"Error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/technicians', methods=['GET'])
@login_required
def api_technicians():
    try:
        from config_mtrx_module.computers import retrieve_all_technicians
        success, message, technicians, status_code = retrieve_all_technicians()
        
        if success:
            technician_list = [{
                "id": tech.id,
                "name": tech.name
            } for tech in technicians]
            
            return app.response_class(
                response=json.dumps(technician_list),
                status=200,
                mimetype='application/json'
            )
        else:
            return app.response_class(
                response=json.dumps({"Error": message}),
                status=status_code,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error in api_technicians: {e}")
        return app.response_class(
            response=json.dumps({"Error": str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/computers')
@login_required
def computers():
    return render_template('computers.html')

def computer_info(computer_name) -> dict:
    # Create a new session for this request to avoid concurrent access issues
    from config_mtrx_module.db import Session
    local_session = Session()
    
    try:
        # Fetch computer record once with all relationships
        computer_record = local_session.query(Computers).filter_by(name=computer_name).first()
        if not computer_record:
            return {"Error": f"Computer '{computer_name}' not found", "code": 404}
        
        computer = {}
        computer["name"] = computer_name
        
        # Fetch profile information
        try:
            computer["profile"] = {"name": computer_record.profile.name} if computer_record.profile else None
        except Exception as e:
            print(f"Error fetching profile for {computer_name}: {e}")
            return {"Error": f"Profile fetch failed: {str(e)}", "code": 500}

        # Fetch progress information
        try:
            completed_steps = computer_record.setup_steps
            profile = computer_record.profile
            
            if not profile:
                return {"Error": f"No profile associated with '{computer_name}'", "code": 404}
            
            total_steps = profile.setup_steps_to_follow
            remaining_steps = [step for step in total_steps if step not in completed_steps]
            
            computer["completed_steps_num"] = len(completed_steps)
            computer["remaining_steps_num"] = len(remaining_steps)
            computer["total_step_num"] = len(remaining_steps) + len(completed_steps)
            computer["completed_steps"] = [step.name for step in completed_steps]
            computer["remaining_steps"] = [step.name for step in remaining_steps]
        except Exception as e:
            print(f"Error fetching progress for {computer_name}: {e}")
            return {"Error": f"Progress fetch failed: {str(e)}", "code": 500}
        
        # Fetch technician information
        try:
            if not computer_record.technician_id: # type: ignore
                computer["technician"] = None
            else:
                technician = computer_record.technician
                computer["technician"] = {"name": technician.name} if technician else None
        except Exception as e:
            print(f"Error fetching technician for {computer_name}: {e}")
            return {"Error": f"Technician fetch failed: {str(e)}", "code": 500}
        
        # Fetch deadline information
        try:
            deadline = computer_record.deadline
            if deadline: # type: ignore
                try:
                    computer["deadline"] = deadline.strftime("%Y-%m-%d %H:%M:%S")
                except (AttributeError, TypeError):
                    # If deadline is not a datetime object, convert to string
                    computer["deadline"] = str(deadline)
            else:
                computer["deadline"] = None
        except Exception as e:
            print(f"Error fetching deadline for {computer_name}: {e}")
            return {"Error": f"Deadline fetch failed: {str(e)}", "code": 500}
        
        return computer
    except Exception as e:
        print(f"Unexpected error in computer_info for {computer_name}: {e}")
        return {"Error": f"Unexpected error: {str(e)}", "code": 500}
    finally:
        # Always close the local session
        local_session.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=9999)

# FOR FUTURE MITZ

# You were creating an api endpoint which retrieves all info about a computer
    # More specifically you were about to implement the function for fetching the computer technician
        # After that you were going to add similar logic for the deadline