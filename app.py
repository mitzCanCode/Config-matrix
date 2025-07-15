from flask import Flask, Response, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from werkzeug.wrappers.response import Response
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import secrets
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin
from functools import wraps

# Config Matrix module imports
from config_mtrx_module.utils import validate_password, StatusCodes
from config_mtrx_module.technicians import create_technician, verify_user, retrieve_all_technicians
from config_mtrx_module.db import  Technicians, get_db_session
from config_mtrx_module.computers import (
    create_computer, toggle_step, edit_computer_name, edit_computer_deadline,
    get_computer_progress, assign_technicians_to_computer, assign_profile_to_computer,
    edit_computer_notes, delete_computer, retrieve_all_computers, computer_info
)
# from config_mtrx_module.db import Session
from config_mtrx_module.profiles import retrieve_all_profiles, get_profile_steps, create_profile, delete_profile

### App set up

# Creating a web application instance
app = Flask(__name__)
# Set the secret key for securely signing the session cookies and CSRF tokens
app.secret_key = secrets.token_hex(16) # Generate a secure random 32-character hex key
# Set db location for Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///computers.db"
# Making session cookies be able to only be sent over secure HTTPS connections
app.config['SESSION_COOKIE_SECURE'] = False # PROD: Set to true
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

    def validate_password(self, field):
        password_validation_response = validate_password(password=field.data)
        
        # If a response is returned then the password is invalid.
        if password_validation_response:
            raise ValidationError(password_validation_response)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


def json_response(data, status_code=200):
    return app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype='application/json'
    )

def error_response(error_message, status_code=500):
    return json_response({"Error": error_message}, status_code)

def handle_api_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Error in {f.__name__}: {e}")
            return error_response(str(e), 500)
    return decorated_function


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        with get_db_session() as session:
            technician = session.query(Technicians).filter_by(id=int(user_id)).first()
            
            if technician:
                # Access attributes while session is active
                technician_id = technician.id
                technician_name = technician.name
                return User(technician_id, technician_name)
        return None
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

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
            with get_db_session() as session:
                technician = session.query(Technicians).filter_by(name=username).first()
                if technician:
                    # Access attributes while session is active
                    technician_id = technician.id
                    technician_name = technician.name
                    user = User(technician_id, technician_name)
                    login_user(user)
                    flash('Login successful!', 'success')
                    
                    # Handle the next parameter safely
                    next_page = request.args.get('next')
                    if next_page:
                        # Validate the next URL to prevent open redirects
                        if urlparse(next_page).netloc == '':
                            # Only allow relative URLs (same domain)
                            return redirect(urljoin(request.host_url, next_page))
                    
                    # Default redirect to dashboard
                    return redirect(url_for('dashboard'))
                else:
                    flash('User not found in database', 'error')
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
@handle_api_errors
def api_computer_info(computer_name) -> Response:
    computer_data = computer_info(computer_name)
    if "Error" in computer_data:
        return error_response(computer_data["Error"], computer_data.get("code", 500))
    return json_response(computer_data)


@app.route('/api/computers', methods=['GET'])
@login_required
@handle_api_errors
def api_computers() -> Response:
    success, message, computers, status_code = retrieve_all_computers()
            
    if success:
        # computers is now a list of dictionaries, not SQLAlchemy objects
        return json_response(computers)
    else:
        return error_response(message, status_code)

@app.route('/api/add_computer', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def add_api_computers():
    data = request.get_json()

    # Extract and validate the parameters
    name = data.get('name')
    deadline_str = data.get('deadline')
    profile_id = data.get('profile_id')
    technician_ids = data.get('technician_ids', [])
            

    if not all([name, deadline_str, profile_id is not None, technician_ids]):
        missing = []
        if not name: missing.append('name')
        if not deadline_str: missing.append('deadline')
        if profile_id is None: missing.append('profile_id')
        if not technician_ids: missing.append('technician_ids')
        print(f"Missing parameters: {missing}")
        raise ValueError(f"Missing parameters: {', '.join(missing)}")

    # Convert deadline to datetime
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError("Deadline must be in 'YYYY-MM-DD HH:MM:SS' format.")

    # Validate profile_id and technician_ids are integers
    try:
        profile_id = int(profile_id)
        technician_ids = [int(tid) for tid in technician_ids]
    except (ValueError, TypeError):
        raise ValueError("profile_id and technician_ids must be valid integers.")

    # Call create_computer
    _, message, status_code = create_computer(
        name=name, deadline=deadline, profile_id=profile_id, technician_ids=technician_ids
    )

    return json_response({'message': message}, status_code)

@app.route('/api/profiles', methods=['GET'])
@login_required
@handle_api_errors
def api_profiles() -> Response:
    # Get profiles data directly from database with session management
    try:
        from config_mtrx_module.db import Profiles, SetupSteps
        
        with get_db_session() as session:
            profiles = session.query(Profiles).all()
            
            profile_list = []
            for profile in profiles:
                # Access profile attributes while session is active
                profile_id = profile.id
                profile_name = profile.name
                profile_description = getattr(profile, 'description', '')
                
                # Get steps for this profile within the same session
                profile_steps = profile.setup_steps_to_follow
                steps_data = []
                for step in profile_steps:
                    steps_data.append({
                        "id": step.id,
                        "name": step.name,
                        "download_link": step.download_link
                    })
                
                profile_list.append({
                    "id": profile_id,
                    "name": profile_name,
                    "description": profile_description,
                    "steps": steps_data,
                    "step_count": len(steps_data)
                })
                
        return json_response(profile_list)
        
    except Exception as e:
        print(f"Error in api_profiles: {e}")
        return error_response("Failed to retrieve profiles", 500)

@app.route('/api/technicians', methods=['GET'])
@login_required
@handle_api_errors
def api_technicians() -> Response:
    success, message, technicians, status_code = retrieve_all_technicians()

    if success:
        technician_list = [{
        "id": tech.id,
        "name": tech.name
        } for tech in technicians]
        
        return json_response(technician_list)
    else:
        return error_response(message, status_code)

@app.route('/api/add_profile', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def add_api_profile() -> Response:
    data = request.get_json()
    
    # Extract and validate the parameters
    name = data.get('name')
    
    if not name:
        return error_response("Missing profile name", 400)
    
    # Call create_profile
    success, message, status_code = create_profile(name=name)
    
    return json_response({
        'success': success,
        'message': message
    }, status_code)

@app.route('/api/profile/<int:profile_id>', methods=['GET'])
@login_required
@handle_api_errors
def api_get_profile(profile_id: int) -> Response:
    """Get detailed profile information including steps"""
    try:
        from config_mtrx_module.db import Profiles, SetupSteps
        
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            
            if not profile:
                return error_response("Profile not found", 404)
            
            # Get profile steps - access the relationship while session is active
            profile_steps = profile.setup_steps_to_follow
            steps_data = []
            for step in profile_steps:
                steps_data.append({
                    "id": step.id,
                    "name": step.name,
                    "download_link": step.download_link or ""
                })
            
            # Get all steps to find available ones
            all_steps = session.query(SetupSteps).all()
            
            # Get steps already assigned to this profile
            assigned_step_ids = [step.id for step in profile_steps]
            
            # Filter out already assigned steps
            available_steps_data = []
            for step in all_steps:
                if step.id not in assigned_step_ids:
                    available_steps_data.append({
                        "id": step.id,
                        "name": step.name,
                        "download_link": step.download_link or ""
                    })
            
            profile_data = {
                "id": profile.id,
                "name": profile.name,
                "steps": steps_data,
                "available_steps": available_steps_data,
                "step_count": len(steps_data)
            }
            
            return json_response(profile_data)
            
    except Exception as e:
        print(f"Error in api_get_profile: {e}")
        return error_response("Failed to retrieve profile", 500)

@app.route('/api/profile/<int:profile_id>/steps', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_add_step_to_profile(profile_id: int) -> Response:
    """Add a step to a profile"""
    from config_mtrx_module.profiles import add_step_to_profile_by_id
    
    data = request.get_json()
    step_id = data.get('step_id')
    
    if not step_id:
        return error_response("Missing step ID", 400)
    
    try:
        step_id = int(step_id)
    except ValueError:
        return error_response("Invalid step ID", 400)
    
    success, message, status_code = add_step_to_profile_by_id(profile_id, step_id)
    
    return json_response({
        'success': success,
        'message': message
    }, status_code)

@app.route('/api/profile/<int:profile_id>/steps/<int:step_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@handle_api_errors
def api_remove_step_from_profile(profile_id: int, step_id: int) -> Response:
    """Remove a step from a profile"""
    from config_mtrx_module.profiles import remove_step_from_profile_by_id
    
    success, message, status_code = remove_step_from_profile_by_id(profile_id, step_id)
    
    return json_response({
        'success': success,
        'message': message
    }, status_code)

@app.route('/api/steps/<int:step_id>', methods=['PUT'])
@csrf.exempt
@login_required
@handle_api_errors
def api_edit_step(step_id: int) -> Response:
    """Edit a step's name and/or download link"""
    from config_mtrx_module.steps import edit_step
    
    data = request.get_json()
    name = data.get('name')
    download_link = data.get('download_link')
    
    if not name and download_link is None:
        return error_response("At least one field (name or download_link) must be provided", 400)
    
    success, message, status_code = edit_step(step_id, name, download_link)
    
    return json_response({
        'success': success,
        'message': message
    }, status_code)

@app.route('/api/steps/<int:step_id>/delete', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_delete_step_from_profile(step_id: int) -> Response:
    """Delete a step if it's not used by any profiles"""
    from config_mtrx_module.steps import can_delete_step, delete_step
    from config_mtrx_module.db import SetupSteps
    
    # Check if step can be deleted
    success, message, can_delete, status_code = can_delete_step(step_id)
    
    if not success:
        return json_response({
            'success': False,
            'message': message
        }, status_code)
    
    if not can_delete:
        return json_response({
            'success': False,
            'message': message
        }, 409)  # Conflict
    
    # Get step name before deletion
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(id=step_id).first()
            if not step:
                return error_response("Step not found", 404)
            step_name = step.name
    except Exception as e:
        return error_response("Error accessing step", 500)
    
    # Delete the step
    success, message, status_code = delete_step(step_name) # type: ignore
    
    return json_response({
        'success': success,
        'message': message
    }, status_code)

@app.route('/api/steps', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_create_step() -> Response:
    """Create a new step"""
    from config_mtrx_module.steps import create_step
    
    data = request.get_json()
    name = data.get('name')
    download_link = data.get('download_link', '')
    
    if not name:
        return error_response("Step name is required", 400)
    
    success, message, status_code = create_step(name, download_link)
    
    # If successful, get the created step's ID
    step_id = None
    if success:
        try:
            from config_mtrx_module.db import SetupSteps
            with get_db_session() as session:
                step = session.query(SetupSteps).filter_by(name=name).first()
                if step:
                    step_id = step.id
        except Exception as e:
            print(f"Error retrieving created step ID: {e}")
    
    return json_response({
        'success': success,
        'message': message,
        'step_id': step_id
    }, status_code)

@app.route('/api/steps/create-and-add', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_create_step_and_add_to_profile() -> Response:
    """Create a new step and immediately add it to a profile"""
    from config_mtrx_module.steps import create_step
    from config_mtrx_module.profiles import add_step_to_profile_by_id
    from config_mtrx_module.db import SetupSteps
    
    data = request.get_json()
    name = data.get('name')
    download_link = data.get('download_link', '')
    profile_id = data.get('profile_id')
    
    if not name:
        return error_response("Step name is required", 400)
    
    if not profile_id:
        return error_response("Profile ID is required", 400)
    
    try:
        profile_id = int(profile_id)
    except ValueError:
        return error_response("Invalid profile ID", 400)
    
    # Create the step
    success, message, status_code = create_step(name, download_link)
    
    if not success:
        return json_response({
            'success': success,
            'message': message
        }, status_code)
    
    # Get the created step's ID
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(name=name).first()
            if not step:
                return error_response("Failed to retrieve created step", 500)
            step_id = step.id
    except Exception as e:
        return error_response("Error retrieving created step", 500)
    
    # Add the step to the profile
    success, message, status_code = add_step_to_profile_by_id(profile_id, step_id) # type: ignore
    
    return json_response({
        'success': success,
        'message': message,
        'step_id': step_id
    }, status_code)

@app.route('/computers')
@login_required
def computers():
    return render_template('computers.html')

@app.route('/profiles')
@login_required
def profiles():
    return render_template('profiles.html')

@app.route('/edit-profile/<int:profile_id>')
@login_required
def edit_profile(profile_id):
    return render_template('edit_profile.html', profile_id=profile_id)

@app.route('/setup/<computer_name>')
@login_required
def setup_computer(computer_name):
    return render_template('setup.html', computer_name=computer_name)

@app.route('/api/computer_setup/<computer_name>', methods=['GET'])
@login_required
@handle_api_errors
def api_computer_setup(computer_name) -> Response: # Get detailed computer setup information including steps
    # Get basic computer info
    computer_data = computer_info(computer_name)
    if "Error" in computer_data:
        return error_response(computer_data["Error"], computer_data.get("code", 500))
            
    # Get detailed progress information
    progress_status, progress_data, progress_code = get_computer_progress(computer_name)
    if not progress_status:
        return error_response(progress_data, progress_code)
            
    # Steps are now already serialized as dictionaries from get_computer_progress
    completed_steps = progress_data["completed_steps"]
    remaining_steps = progress_data["remaining_steps"]
            
    computer_data["detailed_completed_steps"] = completed_steps
    computer_data["detailed_remaining_steps"] = remaining_steps
            
    return json_response(computer_data)

@app.route('/api/toggle_step', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_toggle_step() -> Response: # Toggle completion status of a setup step
    data = request.get_json()
    computer_name = data.get('computer_name')
    step_name = data.get('step_name')
    
    if not all([computer_name, step_name]):
        return error_response("Missing required parameters", StatusCodes.bad_request)
    
    success, message, status_code = toggle_step(computer_name, step_name)
    
    return json_response({
        "success": success,
        "message": message
    }, status_code)

@app.route('/api/edit_computer', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_edit_computer() -> Response:  # Edit computer details (name, deadline, technician)
    data = request.get_json()
    current_name = data.get('current_name')
    field = data.get('field')  # 'name', 'deadline', or 'technician'
    value = data.get('value')
    
    if not all([current_name, field, value is not None]):
        return error_response("Missing required parameters", 400)
    
    if field == 'name':
        success, message, status_code = edit_computer_name(current_name, value)
    elif field == 'deadline':
        try:
            # Parse datetime from string
            deadline = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            success, message, status_code = edit_computer_deadline(current_name, deadline)
        except ValueError:
            return error_response("Invalid deadline format. Use YYYY-MM-DD HH:MM:SS", 400)
    elif field == 'technician':
        try:
            if value is None or value == '' or value == 'null':
                # Unassign all technicians
                success, message, status_code = assign_technicians_to_computer(current_name, [])
            else:
                # Expect value to be a list of technician IDs
                if not isinstance(value, list):
                    return error_response("Technician value must be a list of technician IDs", 400)
                technician_ids = [int(tid) for tid in value]
                success, message, status_code = assign_technicians_to_computer(current_name, technician_ids)
        except ValueError:
            return error_response("Invalid technician ID(s)", 400)
    elif field == 'profile':
        try:
            profile_id = int(value)
            success, message, status_code = assign_profile_to_computer(current_name, profile_id)
        except ValueError:
            return error_response("Invalid profile ID", 400)
    elif field == 'notes':
        success, message, status_code = edit_computer_notes(current_name, value or "")
    else:
        return error_response("Invalid field. Must be 'name', 'deadline', 'technician', 'profile', or 'notes'", 400)
    
    return json_response({
        "success": success,
        "message": message
    }, status_code)

@app.route('/api/delete_computer', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_delete_computer() -> Response:
    data = request.get_json()
    computer_name = data.get('computer_name')
    
    if not computer_name:
        return error_response("Missing computer name", 400)
    
    success, message, status_code = delete_computer(computer_name)
    
    return json_response({
        "success": success,
        "message": message
    }, status_code)

@app.route('/api/delete_profile', methods=['POST'])
@csrf.exempt
@login_required
@handle_api_errors
def api_delete_profile() -> Response:
    """Delete a profile and all its associated computers"""
    data = request.get_json()
    profile_name = data.get('profile_name')
    
    if not profile_name:
        return error_response("Missing profile name", 400)
    
    success, message, status_code = delete_profile(profile_name)
    
    return json_response({
        "success": success,
        "message": message
    }, status_code)

@app.route('/api/profile/<int:profile_id>/computers', methods=['GET'])
@login_required
@handle_api_errors
def api_profile_computers(profile_id: int) -> Response:
    """Get all computers associated with a profile"""
    try:
        from config_mtrx_module.db import Profiles, Computers
        
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            
            if not profile:
                return error_response("Profile not found", 404)
            
            # Get computers for this profile
            computers = session.query(Computers).filter_by(profile_id=profile_id).all()
            
            computer_list = []
            for computer in computers:
                computer_list.append({
                    "id": computer.id,
                    "name": computer.name,
                    "deadline": computer.deadline.isoformat() if computer.deadline else None, # type: ignore
                    "notes": computer.notes or ""
                })
            
            return json_response({
                "profile_id": profile_id,
                "profile_name": profile.name,
                "computers": computer_list,
                "computer_count": len(computer_list)
            })
            
    except Exception as e:
        print(f"Error in api_profile_computers: {e}")
        return error_response("Failed to retrieve profile computers", 500)

@app.route('/api/profile/<int:profile_id>/delete', methods=['DELETE'])
@csrf.exempt
@login_required
@handle_api_errors
def api_delete_profile_by_id(profile_id: int) -> Response:
    """Delete a profile by ID (REST-style endpoint)"""
    try:
        from config_mtrx_module.db import Profiles
        
        # First get the profile name
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            
            if not profile:
                return error_response("Profile not found", 404)
            
            profile_name = profile.name
        
        # Now delete using the existing function
        success, message, status_code = delete_profile(profile_name) # type: ignore
        
        return json_response({
            "success": success,
            "message": message
        }, status_code)
        
    except Exception as e:
        print(f"Error in api_delete_profile_by_id: {e}")
        return error_response("Failed to delete profile", 500)

@app.route('/api/profile/<profile_name>/delete', methods=['DELETE'])
@csrf.exempt
@login_required
@handle_api_errors
def api_delete_profile_by_name(profile_name: str) -> Response:
    """Delete a profile by name (REST-style endpoint)"""
    success, message, status_code = delete_profile(profile_name)
    
    return json_response({
        "success": success,
        "message": message
    }, status_code)


# Used for user logout. When the user logs out they are redirected to the login page
@app.route('/logout')
# User need to be logged in
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=9999)
