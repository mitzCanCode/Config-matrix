from .db import get_db_session, session, Technicians
import bcrypt

# Create technician
def create_technician(name: str, password: str) -> tuple:
    try:
        with get_db_session() as session:
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
            return (True, f"User '{name}' was created", 200)
    
    except Exception as e:
        print(f"\033[31m{e}\033[0m")
        return (False, f"User '{name}' creation failed", 500)

# Check if user is valid (sign in checker)
def verify_user(name: str, password: str) -> tuple:
    with get_db_session() as session:
        user = session.query(Technicians).filter_by(name=name).first()
        if not user:
            return (False, f"User '{name}' does not exist", 404)
        stored_hash = user.password.encode()
        bytes_pass = password.encode()
        
        if bcrypt.checkpw(bytes_pass, stored_hash):
            return (True, "Sign in successful", 200)
        else:
            return (False, "Invalid password", 401)

# Retrieve all technicians from the database
def retrieve_all_technicians() -> tuple:
    try:
        technicians = session.query(Technicians).all()
        if technicians:
            return (True, "Technicians retrieved successfully", technicians, 200)
        else:
            return (True, "No technicians have been created yet", technicians, 200)
    except Exception as e:
        print(e)
        return (False, "An error occurred while retrieving technicians", [], 500)
