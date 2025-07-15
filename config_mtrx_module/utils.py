### General imports:
from datetime import datetime # Used for create_time
import re # Used for validate_password

class StatusCodes:
    success = 200
    created = 201
    accepted = 202
    no_content = 204

    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    conflict = 409

    internal_server_error = 500
    not_implemented = 501
    bad_gateway = 502
    service_unavailable = 503

# Custom validator for password strength
def validate_password(password) -> str:
    # Check password length    
    if len(password) < 8 or len(password) > 12:
        return 'Password must be between 8 and 12 characters long.'
    
    re_password_checks = [
        (r'[A-Z]', 'Password must contain at least one uppercase letter.'),
        (r'[a-z]', 'Password must contain at least one lowercase letter.'),
        (r'[0-9]', 'Password must contain at least one number.'),
        (r'[!@#\$%\^\&\*]', 'Password must contain at least one special character: !, @, #, $, %, etc.')
    ]
            
    # Testing password over all the password checks
    for password_check, message in re_password_checks:
        if not re.search(password_check, password):
            return message # Return error message if password is invalid

    return '' # If password is valid return nothing


def general_exception(error_user_return: tuple, error_message_server: Exception) -> tuple:
    print(error_message_server)
    return error_user_return