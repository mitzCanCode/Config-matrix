from db import session, Computers, SetupSteps, Profiles
from datetime import datetime

def mark_step_complete(computer_name: str, step_name: str) -> tuple:
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        step = session.query(SetupSteps).filter_by(name=step_name).first()

        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        if not step:
            return (False, f"Setup step '{step_name}' not found", 404)

        if step in computer.setup_steps:
            return (False, f"Step '{step_name}' already marked as complete for '{computer_name}'", 409)

        computer.setup_steps.append(step)
        session.commit()
        return (True, f"Marked step '{step_name}' as complete for '{computer_name}'", 200)

    except Exception as e:
        print(e)
        session.rollback()
        return (False, "Error marking step as complete", 500)

def mark_step_incomplete(computer_name: str, step_name: str) -> tuple:
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        step = session.query(SetupSteps).filter_by(name=step_name).first()

        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        if not step:
            return (False, f"Setup step '{step_name}' not found", 404)

        if step not in computer.setup_steps:
            return (False, f"Step '{step_name}' not marked as complete for '{computer_name}'", 404)

        computer.setup_steps.remove(step)
        session.commit()
        return (True, f"Marked step '{step_name}' as incomplete for '{computer_name}'", 200)

    except Exception as e:
        print(e)
        session.rollback()
        return (False, "Error marking step as incomplete", 500)

def get_computer_progress(computer_name: str) -> tuple:
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)

        completed_steps = computer.setup_steps
        profile = computer.profile

        if not profile:
            return (False, f"No profile associated with '{computer_name}'", 404)

        total_steps = profile.setup_steps_to_follow
        remaining_steps = [step for step in total_steps if step not in completed_steps]

        return (True, {
            "completed_steps": completed_steps,
            "remaining_steps": remaining_steps
        }, 200)

    except Exception as e:
        print(e)
        return (False, "Error retrieving computer progress", 500)

def get_remaining_steps(computer_name: str) -> tuple:
    try:
        status, data, code = get_computer_progress(computer_name)
        if not status:
            return (status, data, code)

        return (True, data["remaining_steps"], 200)

    except Exception as e:
        print(e)
        return (False, "Error retrieving remaining steps", 500)

def create_computer(name: str, deadline: datetime, profile_id: int) -> tuple:
    try:
        new_computer = Computers(
            name = name,
            deadline = deadline,
            profile_id = profile_id, 
            setup_steps = []
        )
        session.add(new_computer)
        session.commit()
        return (True, f"Computer ({name}) was created", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Computer ({name}) creation failed", 500)

def retrieve_all_computers() -> tuple:
    try: 
        # Retrieving all computers
        computers = session.query(Computers).all()
        if computers:
            return (True, "Computers retrieved successfully", computers, 200)
        else:
            return (True, "No computers have been created yet", computers, 200)
    except Exception as e:
        return (False, "An error occurred while mapping computers", [], 500)

def edit_computer_name(current_name: str, new_name: str) -> tuple:
    try:
        # Find the computer by current name
        computer = session.query(Computers).filter_by(name=current_name).first()
        if not computer:
            return (False, f"Computer '{current_name}' not found", 404)
        
        # Check if new name already exists
        existing = session.query(Computers).filter_by(name=new_name).first()
        if existing and existing.id != computer.id:
            return (False, f"Computer name '{new_name}' already exists", 409)
        
        # Update the name
        computer.name = new_name
        session.commit()
        
        return (True, f"Computer name changed from '{current_name}' to '{new_name}'", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error updating computer name", 500)

def edit_computer_deadline(computer_name: str, new_deadline: datetime) -> tuple:
    try:
        # Find the computer by name
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        # Store old deadline for confirmation message
        old_deadline = computer.deadline
        
        # Update the deadline
        computer.deadline = new_deadline
        session.commit()
        
        return (True, f"Computer '{computer_name}' deadline changed from {old_deadline} to {new_deadline}", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error updating computer deadline", 500)
