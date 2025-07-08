from db import session, SetupSteps


def create_step(name: str, download_link: str) -> tuple:
    try:
        # Check if step with same name already exists
        existing = session.query(SetupSteps).filter_by(name=name).first()
        if existing:
            return (False, f"Setup step '{name}' already exists", 409)
        
        new_step = SetupSteps(
            name = name,
            download_link = download_link
        )
        session.add(new_step)
        session.commit()
        return (True, f"{name}({download_link}) setup step was created", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"{name}({download_link}) creation failed", 500)

def retrieve_all_steps() -> tuple:
    try: 
        # Retrieving all setup steps
        steps = session.query(SetupSteps).all()
        if steps:
            return (True, "Setup steps retrieved successfully", steps, 200)
        else:
            return (True, "No setup steps have been created yet", steps, 200)
    except Exception as e:
        return (False, "An error occurred while mapping setup steps", [], 500)

def delete_step(step_name: str) -> tuple:
    try:
        step = session.query(SetupSteps).filter_by(name=step_name).first()
        if not step:
            return (False, f"Setup step '{step_name}' not found", 404)
        
        session.delete(step)
        session.commit()
        return (True, f"Setup step '{step_name}' deleted successfully", 200)
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error deleting setup step '{step_name}'", 500)
        
if __name__ == "__main__":
    status, message, error_code = create_step(name="Change computer font", download_link="System Preferences > General > Font")
    print(status, message, error_code)
    status, message, error_code = create_step(name="Install Visual Studio Code", download_link="https://code.visualstudio.com/download")
    print(status, message, error_code)

