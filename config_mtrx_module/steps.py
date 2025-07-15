### Custom module imports:
from .db import get_db_session, SetupSteps
from .utils import StatusCodes


def create_step(name: str, download_link: str) -> tuple:
    try:
        with get_db_session() as session:
            # Check if step with same name already exists
            existing = session.query(SetupSteps).filter_by(name=name).first()
            if existing:
                return (False, f"Setup step '{name}' already exists", StatusCodes.conflict)
            
            new_step = SetupSteps(
                name = name,
                download_link = download_link
            )
            session.add(new_step)
            return (True, f"{name}({download_link}) setup step was created", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"{name}({download_link}) creation failed", StatusCodes.internal_server_error)

def retrieve_all_steps() -> tuple:
    try: 
        with get_db_session() as session:
            # Retrieving all setup steps
            steps = session.query(SetupSteps).all()
            if steps:
                return (True, "Setup steps retrieved successfully", steps, StatusCodes.success)
            else:
                return (True, "No setup steps have been created yet", steps, StatusCodes.success)
    except Exception as e:
        return (False, "An error occurred while mapping setup steps", [], StatusCodes.internal_server_error)

def delete_step(step_name: str) -> tuple:
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(name=step_name).first()
            if not step:
                return (False, f"Setup step '{step_name}' not found", StatusCodes.not_found)
            
            session.delete(step)
            return (True, f"Setup step '{step_name}' deleted successfully", StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, f"Error deleting setup step '{step_name}'", StatusCodes.internal_server_error)
        
def get_remaining_steps(computer_name: str) -> tuple:
    try:
        from .computers import get_computer_progress
        computer_progress = get_computer_progress(computer_name)
        if not computer_progress[0]:
            return computer_progress

        return (True, computer_progress[1]["remaining_steps"], StatusCodes.success)

    except Exception as e:
        print(e)
        return (False, "Error retrieving remaining steps", StatusCodes.internal_server_error)

def edit_step(step_id: int, name: str | None = None, download_link: str | None = None) -> tuple:
    """Edit a step's name and/or download link"""
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(id=step_id).first()
            if not step:
                return (False, f"Setup step with ID {step_id} not found", StatusCodes.not_found)
            
            # Check if new name conflicts with existing steps (excluding current step)
            if name and name != step.name:
                existing = session.query(SetupSteps).filter_by(name=name).first()
                if existing:
                    return (False, f"Setup step '{name}' already exists", StatusCodes.conflict)
                step.name = name # type: ignore
            
            if download_link is not None:
                step.download_link = download_link # type: ignore
            
            return (True, f"Step '{step.name}' updated successfully", StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error updating step", StatusCodes.internal_server_error)

def get_step_usage_count(step_id: int) -> tuple:
    """Get the number of profiles using this step"""
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(id=step_id).first()
            if not step:
                return (False, f"Setup step with ID {step_id} not found", 0, StatusCodes.not_found)
            
            profile_count = len(step.profiles)
            return (True, "Step usage retrieved", profile_count, StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error retrieving step usage", 0, StatusCodes.internal_server_error)

def can_delete_step(step_id: int) -> tuple:
    """Check if a step can be safely deleted (not used by any profiles)"""
    try:
        success, message, usage_count, status_code = get_step_usage_count(step_id)
        if not success:
            return (False, message, status_code)
        
        can_delete = usage_count == 0
        return (True, f"Step can {'be deleted' if can_delete else 'not be deleted (used by {} profiles)'.format(usage_count)}", can_delete, StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error checking step deletion eligibility", False, StatusCodes.internal_server_error)
    

