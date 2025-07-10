from .db import session, Technicians
from .utils import validate_int
import bcrypt
import sys
import re

def create_technician(name: str, password: str) -> tuple:
    try:
        existing = session.query(Technicians).filter_by(name=name).first()
        if existing:
            return (False, f"User '{name}' already exists", 409)

        # Encrypting user password
        bytes_pass = password.encode()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(bytes_pass, salt)

        # Creating technician
        new_technician = Technicians(
            name = name,
            password = hashed_password.decode()
        )
        
        # Adding user to db
        session.add(new_technician)
        session.commit()
        return (True, f"User '{name}' was created", 200)
    
    except Exception as e:
        print(f"\033[31m{e}\033[0m")
        session.rollback()
        return (False, f"User '{name}' creation failed", 500)

def verify_user(name: str, password: str) -> tuple:
    user = session.query(Technicians).filter_by(name=name).first()
    if not user:
        return (False, f"User '{name}' does not exist", 404)
    stored_hash = user.password.encode()
    bytes_pass = password.encode()
    
    if bcrypt.checkpw(bytes_pass, stored_hash):
        return (True, "Sign in successful", 200)
    else:
        return (False, "Invalid password", 401)

def sign_in_sign_up_cli() -> tuple:
    help = "1) Sign up\n2) Sign in\n3) Exit"
    while True:
            
        print(f"\033[94m{help}\033[0m")
        choice, cancelled = validate_int(value_name="login option", value_from=1, value_to=3, indentation_lvl=0)
        if cancelled:
            print("\033[31mExiting Config matrix\033[0m")
            sys.exit()
        if choice == 1:
            try:
                print("\033[36mSignup process initiated\033[0m")
                username = input("\tUsername: ")
                
                while True:
                    password1 = input("\tPassword: ")
                    
                    if len(password1) < 8 or len(password1) > 12:
                        print("\033[31mPassword must be between 8 and 12 characters long.\033[0m")
                        continue
                
                    if not re.search(r'[A-Z]', password1):
                        print("\033[31mPassword must contain at least one uppercase letter.\033[0m")
                        continue
                
                    if not re.search(r'[a-z]', password1):
                        print("\033[31mPassword must contain at least one lowercase letter.\033[0m")
                        continue
                    
                    if not re.search(r'[0-9]', password1):
                        print("\033[31mPassword must contain at least one number.\033[0m")
                        continue
                    
                    break
                while True:
                    password2 = input("\tConfirm password: ")
                    if password1 == password2:
                        password = password1
                        break
                    else:
                        print("\033[31mPasswords do not match. Please try again.\033[0m")
                        continue
                
            except KeyboardInterrupt:
                print("\n\033[36mCancelling sign up process...\033[0m")
                continue
                    
            success, message, code = create_technician(name=username, password=password1)
            if success:
                print(f"\033[92m{message}\033[0m")
            else:
                print(f"\033[31m{message}\033[0m")

            if not success:
                continue

            print("\033[92mYou will now be automatically signed in with your new account.\033[0m")
            return (True, message, username, password1, code)
        
        elif choice == 2:
            try:
                username = input("\tUsername: ")
                password = input("\tPassword: ")
                success, message, _ = verify_user(name = username, password=password)
                if success:
                    print(f"\033[92m{message}\033[0m")
                else:
                    print(f"\033[31m{message}\033[0m")
                
                attempts = 0
                while not success and attempts < 3:
                    print("\033[33mTry again:\033[0m")
                    username = input("\tUsername: ")
                    password = input("\tPassword: ")
                    success, message, _ = verify_user(name=username, password=password)
                    if success:
                        print(f"\033[92m{message}\033[0m")
                    else:
                        print(f"\033[31m{message}\033[0m")
                    attempts += 1

                if not success:
                    print("\033[31mLogin failed after 3 attempts\nShutting down...\033[0m")
                    sys.exit()
                    
            except KeyboardInterrupt:
                print("\n\033[36mCancelling login process...\033[0m")
                continue
            
            return (True, "User logged in successfully", username, password, 200)
        else:
            print("\033[31mExiting Config matrix\033[0m")
            sys.exit()

### FOR FUTURE MITZ

# You were creating a function to verify user login
# After that you were going to add a technician command in the cli to create users
# You also need to add a way to assign a technitian to computers