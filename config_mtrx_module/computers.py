### Custom module imports:
from .db import session, Computers, SetupSteps
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
  name     - Edit computer name
  deadline - Edit computer deadline
  exit     - Exit computer editing
"""



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
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Type 'help' for available options.\033[0m")
            
            
def computer_prompt() -> None:
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

            status, message, _ = create_computer(computer_name, deadline, selected_profile.id)
            if status:
                print(f"\t\033[94m{message}\033[0m")
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "show":
            status, message, computers, _ = retrieve_all_computers()
            if not status:
                print(message) 
                continue
            if not computers:
                print(message)
            else:
                for index, computer in enumerate(computers):
                    profile_name = computer.profile.name if computer.profile else "No Profile"
                    print(f"\t\033[94m{index + 1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m")
                    
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
                    print(f"\t\033[94m{index + 1}. {computer.name} ({profile_name})\033[0m, \033[36mDue by: {computer.deadline}\033[0m")
                    
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
