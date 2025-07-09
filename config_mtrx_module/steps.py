### Custom module imports:
from .db import session, SetupSteps
from .utils import validate_int

setup_step_help = """
\033[94mSetup Step commands:\033[0m
  new    - Create a new setup step
  show   - Display all setup steps
  delete - Delete a setup step
  exit   - Exit setup step management
"""

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
        
def get_remaining_steps(computer_name: str) -> tuple:
    try:
        from computers import get_computer_progress
        status, data, code = get_computer_progress(computer_name)
        if not status:
            return (status, data, code)

        return (True, data["remaining_steps"], 200)

    except Exception as e:
        print(e)
        return (False, "Error retrieving remaining steps", 500)
    
def setup_step_prompt() -> None:
    while True:
        try:
            prompt = input("Config Matrix/Setup Steps ->")
            prompt = prompt.strip().lower()
        except KeyboardInterrupt:
            print("\n\033[36mReturning to main menu...\033[0m")
            break
        if prompt == "help":
            print("\033[94m" + setup_step_help + "\033[0m")
        elif prompt == "new":
            try:
                step_name = input("\tSetup step name:").strip()
                instructions = input("\tInstructions/Link:").strip()
            except KeyboardInterrupt:
                print("\n\t\033[36mStep creation cancelled.\033[0m")
                continue
            status, message, _ = create_step(name=step_name, download_link=instructions)
            if status:
                print(f"\t\033[94m{message}\033[0m")
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "show":
            status, message, steps, _ = retrieve_all_steps()
            if not status:
                print(message) 
                continue
            if not steps:
                print(message)
            else:
                for index, step in enumerate(steps):
                    print(f"\t\033[94m{index + 1}. {step.name}\033[0m(\033[36m{step.download_link}\033[0m)")
        elif prompt == "delete":
            status, message, all_steps, _ = retrieve_all_steps()
            if not status or not all_steps:
                print("\033[31mNo setup steps available to delete.\033[0m")
                continue
            
            # Get all profiles to determine which steps are used in profiles
            from profiles import retrieve_all_profiles, get_profile_steps
            profile_status, profile_message, profiles, _ = retrieve_all_profiles()
            used_step_names = set()
            if profile_status and profiles:
                for profile in profiles:
                    profile_steps_status, _, profile_steps, _ = get_profile_steps(profile.name)
                    if profile_steps_status and profile_steps:
                        used_step_names.update(step.name for step in profile_steps)
            
            # Separate steps into profile-used steps and unused steps
            profile_used_steps = [step for step in all_steps if step.name in used_step_names]
            unused_steps = [step for step in all_steps if step.name not in used_step_names]
            
            # Initially show only profile-used steps
            print("\033[94mAvailable setup steps:\033[0m")
            
            # Display profile-used steps first (if any)
            if profile_used_steps:
                print("\t\033[93m--- Steps Used in Profiles ---\033[0m")
                for i, step in enumerate(profile_used_steps):
                    print(f"\t\033[36m{i+1}. {step.name}\033[0m \033[37m(used in profiles)\033[0m")
                
                # Ask if user wants to see more steps
                if unused_steps:
                    try:
                        show_more = input("\t\033[94mShow all available steps? (y/N): \033[0m").lower()
                    except KeyboardInterrupt:
                        print("\n\t\033[36mOperation cancelled.\033[0m")
                        continue
                    if show_more == 'y':
                        # Show all steps
                        print("\t\033[93m--- All Available Steps ---\033[0m")
                        ordered_steps = profile_used_steps + unused_steps
                        
                        # Display profile-used steps with indicator
                        for i, step in enumerate(profile_used_steps):
                            print(f"\t\033[36m{i+1}. {step.name}\033[0m \033[37m(used in profiles)\033[0m")
                        
                        # Display unused steps
                        start_index = len(profile_used_steps)
                        for i, step in enumerate(unused_steps):
                            print(f"\t\033[36m{start_index + i + 1}. {step.name}\033[0m")
                        
                        step_index, cancelled = validate_int("step number to delete", 1, len(ordered_steps))
                        if cancelled:
                            continue
                        step_index -= 1
                        selected_step = ordered_steps[step_index]
                    else:
                        # User chose to select from profile-used steps only
                        step_index, cancelled = validate_int("step number to delete", 1, len(profile_used_steps))
                        if cancelled:
                            continue
                        step_index -= 1
                        selected_step = profile_used_steps[step_index]
                else:
                    # Only profile-used steps available
                    step_index, cancelled = validate_int("step number to delete", 1, len(profile_used_steps))
                    if cancelled:
                        continue
                    step_index -= 1
                    selected_step = profile_used_steps[step_index]
            else:
                # No profile-used steps, show unused steps
                if unused_steps:
                    print("\t\033[93m--- Unused Steps ---\033[0m")
                    for i, step in enumerate(unused_steps):
                        print(f"\t\033[36m{i+1}. {step.name}\033[0m")
                    
                    step_index, cancelled = validate_int("step number to delete", 1, len(unused_steps))
                    if cancelled:
                        continue
                    step_index -= 1
                    selected_step = unused_steps[step_index]
                else:
                    # No steps available at all
                    print("\033[31mNo setup steps available to delete.\033[0m")
                    continue
            
            # Confirm deletion
            try:
                confirmation = input(f"\tAre you sure you want to delete '{selected_step.name}'? (y/N): ")
            except KeyboardInterrupt:
                print("\n\t\033[36mDeletion cancelled.\033[0m")
                continue
            if confirmation.lower() == 'y':
                status, message, _ = delete_step(selected_step.name)
                if status:
                    print(f"\t\033[94m{message}\033[0m")
                else:
                    print(f"\t\033[31m{message}\033[0m")
            else:
                print("\t\033[36mDeletion cancelled.\033[0m")
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Run 'help' for setup steps instructions.\033[0m")

if __name__ == "__main__":
    status, message, error_code = create_step(name="Change computer font", download_link="System Preferences > General > Font")
    print(status, message, error_code)
    status, message, error_code = create_step(name="Install Visual Studio Code", download_link="https://code.visualstudio.com/download")
    print(status, message, error_code)

