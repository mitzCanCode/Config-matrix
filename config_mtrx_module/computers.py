### Custom module imports:
from .db import session, Computers, SetupSteps, Technicians
from .utils import create_time, validate_int
from .profiles import retrieve_all_profiles
from .steps import get_remaining_steps

### General imports:
from datetime import datetime


computer_help = """
\033[94mComputer commands:\033[0m
  new       - Create a new computer
  show      - Display all computers
  edit      - Edit an existing computer
  toggle    - Toggle completion status of a setup step
  progress  - View setup progress for a computer
  remaining - View remaining steps for a computer
  exit      - Exit computer management
"""

edit_computer_help = """
\033[94mEdit computer commands:\033[0m
  name       - Edit computer name
  deadline   - Edit computer deadline
  technician - Assign/change technician
  exit       - Exit computer editing
"""

def get_computer_assigned_technician(computer_name: str) -> tuple:
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", None, 404)
        
        if not computer.technician_id: # type: ignore
            return (True, f"No technician assigned to '{computer_name}'", None, 200)
        
        technician = computer.technician
        if technician:
            return (True, f"Technician '{technician.name}' is assigned to '{computer_name}'", technician, 200)
        else:
            return (False, f"Technician data not found for computer '{computer_name}'", None, 404)
    
    except Exception as e:
        print(e)
        return (False, "Error retrieving assigned technician", None, 500)


def get_computer_deadline(computer_name: str) -> tuple:
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", None, 404)
        
        deadline = computer.deadline
        if deadline: # type: ignore
            return (True, f"Computer '{computer_name}' has a deadline on {deadline}", deadline, 200)
        else:
            return (True, f"No deadline set for '{computer_name}'", None, 200)
    
    except Exception as e:
        print(e)
        return (False, "Error retrieving computer deadline", None, 500)



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

def retrieve_computers_by_technician(technician_name: str) -> tuple:
    """Retrieve computers assigned to a specific technician"""
    try:
        # Find technician by name
        technician = session.query(Technicians).filter_by(name=technician_name).first()
        if not technician:
            return (False, f"Technician '{technician_name}' not found", [], 404)
        
        # Retrieve computers assigned to this technician
        computers = session.query(Computers).filter_by(technician_id=technician.id).all()
        if computers:
            return (True, f"Retrieved {len(computers)} computers assigned to '{technician_name}'", computers, 200)
        else:
            return (True, f"No computers assigned to '{technician_name}'", computers, 200)
    except Exception as e:
        print(e)
        return (False, "An error occurred while retrieving computers by technician", [], 500)

def edit_computer_name(current_name: str, new_name: str) -> tuple:
    try:
        # Find the computer by current name
        computer = session.query(Computers).filter_by(name=current_name).first()
        if not computer:
            return (False, f"Computer '{current_name}' not found", 404)
        
        # Check if new name already exists
        existing = session.query(Computers).filter_by(name=new_name).first()
        if existing and existing.id != computer.id:  # type: ignore
            return (False, f"Computer name '{new_name}' already exists", 409)
        
        # Update the name
        computer.name = new_name # type: ignore
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
        computer.deadline = new_deadline # type: ignore
        session.commit()
        
        return (True, f"Computer '{computer_name}' deadline changed from {old_deadline} to {new_deadline}", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error updating computer deadline", 500)

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
    
def create_computer(name: str, deadline: datetime, profile_id: int, technician_name: str) -> tuple:
    try:
        # Find technician by name
        technician = session.query(Technicians).filter_by(name=technician_name).first()
        if not technician:
            return (False, f"Technician '{technician_name}' not found", 404)

        new_computer = Computers(
            name = name,
            deadline = deadline,
            profile_id = profile_id,
            technician_id = technician.id,
            setup_steps = []
        )
        session.add(new_computer)
        session.commit()
        return (True, f"Computer ({name}) was created and assigned to technician {technician_name}", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Computer ({name}) creation failed", 500)

def create_computer_with_multiple_technicians(name: str, deadline: datetime, profile_id: int, technician_ids: list) -> tuple:
    """Create a computer and assign multiple technicians by IDs"""
    try:
        # Check if computer name already exists
        existing_computer = session.query(Computers).filter_by(name=name).first()
        if existing_computer:
            return (False, f"Computer '{name}' already exists", 409)
        
        # Verify technicians exist
        technicians = session.query(Technicians).filter(Technicians.id.in_(technician_ids)).all()
        if not technicians or len(technicians) != len(technician_ids):
            return (False, "Some technician IDs are invalid", 404)
        
        # Check if profile exists
        from .profiles import retrieve_all_profiles
        profile_success, _, profiles, _ = retrieve_all_profiles()
        if not profile_success:
            return (False, "Error retrieving profiles", 500)
        
        profile_exists = any(profile.id == profile_id for profile in profiles)
        if not profile_exists:
            return (False, f"Profile with ID {profile_id} not found", 404)

        new_computer = Computers(
            name = name,
            deadline = deadline,
            profile_id = profile_id,
            setup_steps = []
        )

        # Assign technicians
        new_computer.technicians.extend(technicians)

        session.add(new_computer)
        session.commit()
        technician_names = ', '.join([tech.name for tech in technicians])
        return (True, f"Computer ({name}) was created and assigned to technicians: {technician_names}", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Computer ({name}) creation failed", 500)

def retrieve_all_technicians() -> tuple:
    """Retrieve all technicians from the database"""
    try:
        technicians = session.query(Technicians).all()
        if technicians:
            return (True, "Technicians retrieved successfully", technicians, 200)
        else:
            return (True, "No technicians have been created yet", technicians, 200)
    except Exception as e:
        print(e)
        return (False, "An error occurred while retrieving technicians", [], 500)

def assign_technicians_to_computer(computer_name: str, technician_ids: list) -> tuple:
    """Assign multiple technicians to a computer"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        technicians = session.query(Technicians).filter(Technicians.id.in_(technician_ids)).all()
        if not technicians:
            return (False, "No valid technicians found", 404)
        
        # Clear existing assignments
        computer.technicians = []

        # Assign the technicians
        computer.technicians.extend(technicians)
        session.commit()
        
        technician_names = ', '.join([t.name for t in technicians])
        return (True, f"Computer '{computer_name}' now assigned to technicians: {technician_names}", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, "Error assigning technicians to computer", 500)

def assign_technician_to_computer(computer_name: str, technician_id: int) -> tuple:
    """Assign a technician to a computer (backward compatibility)"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        technician = session.query(Technicians).filter_by(id=technician_id).first()
        if not technician:
            return (False, f"Technician with ID {technician_id} not found", 404)
        
        # Check if computer already has this technician assigned
        if computer.technician_id == technician_id: # type: ignore
            return (False, f"Computer '{computer_name}' is already assigned to '{technician.name}'", 409)
        
        # Store old technician name for confirmation message
        old_technician_name = computer.technician.name if computer.technician else "Unassigned"
        
        # Assign the technician
        computer.technician_id = technician_id # type: ignore
        session.commit()
        
        return (True, f"Computer '{computer_name}' assigned from '{old_technician_name}' to '{technician.name}'", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error assigning technician to computer", 500)

def unassign_technician_from_computer(computer_name: str) -> tuple:
    """Remove technician assignment from a computer"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        if not computer.technician_id: # type: ignore
            return (False, f"Computer '{computer_name}' has no technician assigned", 404)
        
        # Store technician name for confirmation message
        technician_name = computer.technician.name if computer.technician else "Unknown"
        
        # Remove the technician assignment
        computer.technician_id = None # type: ignore
        session.commit()
        
        return (True, f"Technician '{technician_name}' unassigned from computer '{computer_name}'", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error unassigning technician from computer", 500)

def assign_profile_to_computer(computer_name: str, profile_id: int) -> tuple:
    """Assign a profile to a computer"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        # Check if profile exists
        from .profiles import retrieve_all_profiles
        profile_success, _, profiles, _ = retrieve_all_profiles()
        if not profile_success:
            return (False, "Error retrieving profiles", 500)
        
        profile = next((p for p in profiles if p.id == profile_id), None)
        if not profile:
            return (False, f"Profile with ID {profile_id} not found", 404)
        
        # Check if computer already has this profile assigned
        if computer.profile_id == profile_id: # type: ignore
            return (False, f"Computer '{computer_name}' already has profile '{profile.name}' assigned", 409)
        
        # Store old profile name for confirmation message
        old_profile_name = computer.profile.name if computer.profile else "No profile"
        
        # Assign the profile
        computer.profile_id = profile_id # type: ignore
        
        # Clear completed steps since profile changed
        computer.setup_steps = [] # type: ignore
        
        session.commit()
        
        return (True, f"Computer '{computer_name}' profile changed from '{old_profile_name}' to '{profile.name}'. Setup steps have been reset.", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error assigning profile to computer", 500)

def delete_computer(computer_name: str) -> tuple:
    """Delete a computer and all its associated data"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        # Store computer name for confirmation message
        name = computer.name
        
        # Delete the computer (setup steps will be automatically removed due to relationship)
        session.delete(computer)
        session.commit()
        
        return (True, f"Computer '{name}' has been deleted successfully", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error deleting computer '{computer_name}'", 500)

def edit_computer_notes(computer_name: str, notes: str) -> tuple:
    """Edit computer notes"""
    try:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return (False, f"Computer '{computer_name}' not found", 404)
        
        # Update the notes
        computer.notes = notes  # type: ignore
        session.commit()
        
        return (True, f"Notes updated for computer '{computer_name}'", 200)
    
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error updating notes for computer '{computer_name}'", 500)
    
    
    
def edit_computer_prompt(computer_index: int) -> None:
    # Get the computer list again to ensure we have current data
    status, message, computers, _ = retrieve_all_computers()
    if not status or not computers or computer_index >= len(computers):
        print("\033[31mError: Computer not found.\033[0m")
        return
    
    selected_computer = computers[computer_index]
    
    while True:
        try:
            prompt = input(f"Config Matrix/Computers/Edit '{selected_computer.name}' ->")
            prompt = prompt.strip().lower()
        except KeyboardInterrupt:
            print("\n\033[36mReturning to computer menu...\033[0m")
            break
        
        if prompt == "help":
            print(edit_computer_help)
        elif prompt == "name":
            try:
                new_name = input(f"\tEnter new name for '{selected_computer.name}': ")
            except KeyboardInterrupt:
                print("\n\t\033[36mName edit cancelled.\033[0m")
                continue
            if new_name.strip():
                status, message, _ = edit_computer_name(selected_computer.name, new_name.strip())
                if status:
                    print(f"\t\033[94m{message}\033[0m")
                    selected_computer.name = new_name.strip()  # Update local reference
                else:
                    print(f"\t\033[31m{message}\033[0m")
            else:
                print("\t\033[31mName cannot be empty.\033[0m")
        elif prompt == "deadline":
            print("\t\033[94mEnter new deadline:\033[0m")
            new_deadline, cancelled = create_time(indentation_lvl=1)
            if cancelled:
                print("\n\t\033[36mDeadline update cancelled.\033[0m")
                continue
            status, message, _ = edit_computer_deadline(selected_computer.name, new_deadline)
            if status:
                print(f"\t\033[94m{message}\033[0m")
                selected_computer.deadline = new_deadline  # Update local reference
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "technician":
            # Get all technicians
            status, message, technicians, _ = retrieve_all_technicians()
            if not status:
                print(f"\t\033[31m{message}\033[0m")
                continue
            if not technicians:
                print("\t\033[31mNo technicians available. Create technicians first.\033[0m")
                continue
            
            # Show current assignment
            current_tech = selected_computer.technician.name if selected_computer.technician else "Unassigned"
            print(f"\t\033[94mCurrent technician: {current_tech}\033[0m")
            
            # Show available technicians
            print("\t\033[94mAvailable technicians:\033[0m")
            print("\t\033[36m0. Remove current assignment\033[0m")
            for i, tech in enumerate(technicians):
                print(f"\t\033[36m{i+1}. {tech.name}\033[0m")
            
            tech_choice, cancelled = validate_int("technician number", 0, len(technicians), indentation_lvl=1)
            if cancelled:
                print("\n\t\033[36mTechnician assignment cancelled.\033[0m")
                continue
            
            if tech_choice == 0:
                # Remove assignment
                status, message, _ = unassign_technician_from_computer(selected_computer.name)
                if status:
                    print(f"\t\033[94m{message}\033[0m")
                    selected_computer.technician_id = None  # Update local reference
                else:
                    print(f"\t\033[31m{message}\033[0m")
            else:
                # Assign technician
                selected_tech = technicians[tech_choice - 1]
                status, message, _ = assign_technician_to_computer(selected_computer.name, selected_tech.id)
                if status:
                    print(f"\t\033[94m{message}\033[0m")
                    selected_computer.technician_id = selected_tech.id  # Update local reference
                else:
                    print(f"\t\033[31m{message}\033[0m")
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Type 'help' for available options.\033[0m")
            

def computer_prompt(current_user: str = "") -> None:
    while True:
        try:
            prompt = input("Config Matrix/Computers ->")
            prompt = prompt.strip().lower()
        except KeyboardInterrupt:
            print("\n\033[36mReturning to main menu...\033[0m")
            break
        if prompt == "help":
            print(computer_help)
        elif prompt == "new":
            status, message, profiles, _ = retrieve_all_profiles()
            if not status or not profiles:
                print("\033[33mWarning: No profiles have been created to assign a profile to a computer. Create one first.\033[0m")
                continue

            for i, profile in enumerate(profiles):
                print(f"\t\033[36m{i+1}. {profile.name}\033[0m")

            selected_index, cancelled = validate_int(value_name="profile number", value_from=1, value_to=len(profiles))
            if cancelled:
                continue
            selected_index -= 1
            selected_profile = profiles[selected_index]

            try:
                computer_name = input("\tComputer name:").strip()
            except KeyboardInterrupt:
                print("\n\t\033[36mComputer creation cancelled.\033[0m")
                continue
            deadline, cancelled = create_time()
            if cancelled:
                print("\n\t\033[36mComputer creation cancelled.\033[0m")
                continue

            status, message, _ = create_computer(computer_name, deadline, selected_profile.id, current_user)
            if status:
                print(f"\t\033[94m{message}\033[0m")
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "show":
            try:
                choice = input("\t\033[94mShow all computers or only assigned to you? (all/assigned): \033[0m").strip().lower()
            except KeyboardInterrupt:
                print("\n\033[36mOperation cancelled.\033[0m")
                continue
            
            if choice == "assigned" and current_user:
                status, message, computers, _ = retrieve_computers_by_technician(current_user)
            else:
                status, message, computers, _ = retrieve_all_computers()
            
            if not status:
                print(message)
                continue
            if not computers:
                print(message)
            else:
                for index, computer in enumerate(computers):
                    profile_name = computer.profile.name if computer.profile else "No Profile"
                    tech_name = computer.technician.name if computer.technician else "Unassigned"
                    print(f"\t\033[94m{index + 1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m, \033[93mTechnician: {tech_name}\033[0m")
                    
        elif prompt == "edit":
            status, message, computers, _ = retrieve_all_computers()
            if not status:
                print(message) 
                continue
            if not computers:
                print(message)
            else:
                for index, computer in enumerate(computers):
                    profile_name = computer.profile.name if computer.profile else "No Profile"
                    tech_name = computer.technician.name if computer.technician else "Unassigned"
                    print(f"\t\033[94m{index + 1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m, \033[93mTechnician: {tech_name}\033[0m")
                    
            selected_computer, cancelled = validate_int(value_name="computer", value_from=1, value_to=len(computers))
            if cancelled:
                continue
            selected_computer -= 1
            edit_computer_prompt(selected_computer)
        elif prompt == "toggle":
            # Get computers
            status, message, computers, _ = retrieve_all_computers()
            if not status or not computers:
                print("\033[31mNo computers available.\033[0m")
                continue
            
            print("\033[94mAvailable computers:\033[0m")
            for i, computer in enumerate(computers):
                profile_name = computer.profile.name if computer.profile else "No Profile"
                print(f"\t\033[94m{i+1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m")
            
            computer_index, cancelled = validate_int("computer number", 1, len(computers))
            if cancelled:
                continue
            computer_index -= 1
            selected_computer = computers[computer_index]
            
            # Get computer progress
            status, data, _ = get_computer_progress(selected_computer.name)
            if not status:
                print(f"\t\033[31m{data}\033[0m")
                continue
            
            completed_steps = data["completed_steps"]
            remaining_steps = data["remaining_steps"]
            all_steps = completed_steps + remaining_steps
            
            # Show available steps
            print("\033[94mAvailable setup steps:\033[0m")
            for i, step in enumerate(all_steps):
                status_symbol = "✓" if step in completed_steps else "○"
                print(f"\t\033[36m{i+1}. {status_symbol} {step.name}\033[0m")
            
            step_index, cancelled = validate_int("setup step number", 1, len(all_steps))
            if cancelled:
                continue
            step_index -= 1
            selected_step = all_steps[step_index]
            
            # Toggle completion status
            if selected_step in completed_steps:
                status, message, _ = mark_step_incomplete(selected_computer.name, selected_step.name)
            else:
                status, message, _ = mark_step_complete(selected_computer.name, selected_step.name)
            
            if status:
                print(f"\t\033[94m{message}\033[0m")
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "progress":
            # Get computers
            status, message, computers, _ = retrieve_all_computers()
            if not status or not computers:
                print("\033[31mNo computers available.\033[0m")
                continue
            
            print("\033[94mAvailable computers:\033[0m")
            for i, computer in enumerate(computers):
                profile_name = computer.profile.name if computer.profile else "No Profile"
                print(f"\t\033[94m{i+1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m")
            
            computer_index, cancelled = validate_int("computer number", 1, len(computers))
            if cancelled:
                continue
            computer_index -= 1
            selected_computer = computers[computer_index]
            
            # Get computer progress
            status, data, _ = get_computer_progress(selected_computer.name)
            if not status:
                print(f"\t\033[31m{data}\033[0m")
                continue
            
            completed_steps = data["completed_steps"]
            remaining_steps = data["remaining_steps"]
            total_steps = len(completed_steps) + len(remaining_steps)
            
            # Get the computer's profile steps to identify which steps are profile steps
            computer_obj = session.query(Computers).filter_by(name=selected_computer.name).first()
            profile_step_names = set()
            if computer_obj and computer_obj.profile:
                profile_steps = computer_obj.profile.setup_steps_to_follow
                profile_step_names = {step.name for step in profile_steps}
            
            print(f"\n\033[94mProgress for '{selected_computer.name}':\033[0m")
            if total_steps == 0:
                print("\t\033[31mNo steps assigned to this computer's profile.\033[0m")
            else:
                progress_percentage = (len(completed_steps) / total_steps) * 100
                print(f"\t\033[36mProgress: {len(completed_steps)}/{total_steps} steps completed ({progress_percentage:.1f}%)\033[0m")
                
                # Check if there are any profile steps to show the legend
                has_profile_steps = any(step.name in profile_step_names for step in completed_steps + remaining_steps)
                
                if completed_steps:
                    print(f"\t\033[94mCompleted steps:\033[0m")
                    for step in completed_steps:
                        if step.name in profile_step_names:
                            print(f"\t\t\033[32m✓ {step.name}*\033[0m")
                        else:
                            print(f"\t\t\033[32m✓ {step.name}\033[0m")
                
                if remaining_steps:
                    print(f"\t\033[36mRemaining steps:\033[0m")
                    for step in remaining_steps:
                        if step.name in profile_step_names:
                            print(f"\t\t\033[37m○ {step.name}*\033[0m")
                        else:
                            print(f"\t\t\033[37m○ {step.name}\033[0m")
                
                # Show legend if there are profile steps
                if has_profile_steps:
                    print(f"\n\t\033[37m* Profile steps\033[0m")
        elif prompt == "remaining":
            # Get computers
            status, message, computers, _ = retrieve_all_computers()
            if not status or not computers:
                print("\033[31mNo computers available.\033[0m")
                continue
            
            print("\033[94mAvailable computers:\033[0m")
            for i, computer in enumerate(computers):
                profile_name = computer.profile.name if computer.profile else "No Profile"
                print(f"\t\033[94m{i+1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m")
            
            computer_index, cancelled = validate_int("computer number", 1, len(computers))
            if cancelled:
                continue
            computer_index -= 1
            selected_computer = computers[computer_index]
            
            # Get remaining steps
            status, remaining_steps, _ = get_remaining_steps(selected_computer.name)
            if not status:
                print(f"\t\033[31m{remaining_steps}\033[0m")
                continue
            
            print(f"\033[94mRemaining steps for '{selected_computer.name}':\033[0m")
            if not remaining_steps:
                print("\t\033[32mAll steps are completed.\033[0m")
            else:
                for step in remaining_steps:
                    print(f"\t\033[37m○ {step.name}\033[0m")
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Run 'help' for computer instructions.\033[0m")
