### Custom module imports:
from .db import session, Profiles, SetupSteps, Computers
from .utils import validate_int
from .steps import retrieve_all_steps

def add_step_to_profile(profile_name: str, step_name: str) -> tuple:
    step = session.query(SetupSteps).filter_by(name=step_name).first()
    profile = session.query(Profiles).filter_by(name=profile_name).first()
    if not step:
        return (False, "Setup step not found", 404)
    if not profile:
        return (False, "Profile not found", 404)
    
    profile.setup_steps_to_follow.append(step)
    session.commit()
    return (True, f"Added {step.name} to profile {profile.name}", 200)

def create_profile(name: str) -> tuple:
    try:
        existing = session.query(Profiles).filter_by(name=name).first()
        if existing:
            return (False, f"Profile '{name}' already exists", 409)
        
        new_profile = Profiles(
            name = name,
        )
        session.add(new_profile)
        session.commit()
        return (True, f"Profile '{name}' created successfully", 200)
    
    except Exception as e:
        print(e)
        return (False, f"An error occured trying to create '{name}' profile", 500)

def delete_profile(name: str) -> tuple:
    try:
        # Fetch the profile
        profile = session.query(Profiles).filter_by(name=name).first()
        if not profile:
            return (False, f"Profile '{name}' not found", 404)

        # Delete all computers using this profile
        session.query(Computers).filter_by(profile_id=profile.id).delete()

        # Delete the profile itself
        session.delete(profile)
        session.commit()

        return (True, f"Profile '{name}' and its computers deleted", 200)

    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error deleting profile '{name}'", 500)
    
def retrieve_all_profiles() -> tuple:
    try: 
        # Retrieving all profiles
        profiles = session.query(Profiles).all()
        
        if profiles:
            return (True, "Profiles retrieved successfully", profiles, 200)
        else:
            return (True, "No profiles have been created yet", profiles, 200)
    except Exception as e:
        return (False, "An error occurred while mapping profiles", [], 500)

def get_profile_steps(profile_name: str) -> tuple:
    try:
        profile = session.query(Profiles).filter_by(name=profile_name).first()
        if not profile:
            return (False, f"Profile '{profile_name}' not found", [], 404)
        
        steps = profile.setup_steps_to_follow
        return (True, f"Steps for profile '{profile_name}'", steps, 200)
    except Exception as e:
        return (False, "An error occurred while retrieving profile steps", [], 500)

def remove_step_from_profile(profile_name: str, step_name: str) -> tuple:
    try:
        step = session.query(SetupSteps).filter_by(name=step_name).first()
        profile = session.query(Profiles).filter_by(name=profile_name).first()
        
        if not step:
            return (False, "Setup step not found", 404)
        if not profile:
            return (False, "Profile not found", 404)
        
        # Check if step is actually assigned to the profile
        if step not in profile.setup_steps_to_follow:
            return (False, f"Step '{step_name}' is not assigned to profile '{profile_name}'", 404)
        
        # Remove the step from the profile
        profile.setup_steps_to_follow.remove(step)
        session.commit()
        
        return (True, f"Removed {step.name} from profile {profile.name}", 200)
    except Exception as e:
        print(e)
        session.rollback()
        return (False, f"Error removing step from profile", 500)



profile_help = """
\033[94mProfile commands:\033[0m
  new    - Create a new profile
  show   - Display all profiles and their assigned steps
  toggle - Add/remove a setup step to/from a profile
  delete - Delete a profile entirely
  exit   - Exit profile management
"""


def profile_prompt() -> None:
    while True:
        try:
            prompt = input("Config Matrix/Profiles ->")
            prompt = prompt.strip().lower()
        except KeyboardInterrupt:
            print("\n\033[36mReturning to main menu...\033[0m")
            break
        if prompt == "help":
            print(profile_help)
        elif prompt == "new":
            try:
                profile_name = input("\tProfile name:").strip()
            except KeyboardInterrupt:
                print("\n\t\033[36mProfile creation cancelled.\033[0m")
                continue
            status, message, _ = create_profile(name=profile_name)
            if status:
                print(f"\t\033[94m{message}\033[0m")
            else:
                print(f"\t\033[31m{message}\033[0m")
        elif prompt == "show":
            status, message, profiles, _ = retrieve_all_profiles()
            if not status:
                print(message) 
                continue
            if not profiles:
                print(message)
            else:
                for profile in profiles:
                    print(f"\t\033[94m{profile.name}\033[0m")
                    # Show assigned steps for each profile
                    status, message, steps, _ = get_profile_steps(profile.name)
                    if steps:
                        print(f"\t\t\033[36mAssigned steps:\033[0m")
                        for step in steps:
                            print(f"\t\t\t\033[37m{step.name}\033[0m")
                            print(f"\t\t\t\t\033[37m{step.download_link}\033[0m")
                    else:
                        print(f"\t\t\033[37mAssigned steps: None\033[0m")
        elif prompt == "toggle":
            # Show available profiles
            status, message, profiles, _ = retrieve_all_profiles()
            if not status or not profiles:
                print("\033[31mNo profiles available. Create a profile first.\033[0m")
                continue
            
            print("\033[94mAvailable profiles:\033[0m")
            for i, profile in enumerate(profiles):
                print(f"\t\033[36m{i+1}. {profile.name}\033[0m")
            
            profile_index, cancelled = validate_int("profile number", 1, len(profiles))
            if cancelled:
                continue
            profile_index -= 1
            selected_profile = profiles[profile_index]
            
            status, message, all_steps, _ = retrieve_all_steps()
            if not status or not all_steps:
                print("\033[31mNo setup steps available. Create setup steps first.\033[0m")
                continue
            
            # Get steps already assigned to this profile
            profile_status, profile_message, profile_steps, _ = get_profile_steps(selected_profile.name)
            profile_step_names = [step.name for step in profile_steps] if profile_status and profile_steps else []
            ordered_steps = all_steps
            
            # Display all steps
            print("\033[94mAvailable setup steps:\033[0m")
            for i, step in enumerate(ordered_steps):
                assigned_str = "(assigned)" if step.name in profile_step_names else ""
                print(f"\t\033[36m{i+1}. {step.name}\033[0m \033[37m{assigned_str}\033[0m")
            
            step_index, cancelled = validate_int("setup step number to toggle", 1, len(ordered_steps))
            if cancelled:
                continue
            step_index -= 1
            selected_step = ordered_steps[step_index]
            step_name = selected_step.name
            
            # Toggle step in profile
            if step_name in profile_step_names:
                status, message, _ = remove_step_from_profile(selected_profile.name, step_name)
                if status:
                    print(f"\t\033[94mRemoved {step_name} from {selected_profile.name}.\033[0m")
                else:
                    print(f"\t\033[31m{message}\033[0m")
            else:
                status, message, _ = add_step_to_profile(selected_profile.name, step_name)
                if status:
                    print(f"\t\033[94mAdded {step_name} to {selected_profile.name}.\033[0m")
                else:
                    print(f"\t\033[31m{message}\033[0m")
        elif prompt == "delete":
            status, message, profiles, _ = retrieve_all_profiles()
            if not status or not profiles:
                print("\033[31mNo profiles available to delete.\033[0m")
                continue
            
            print("\033[94mAvailable profiles:\033[0m")
            for i, profile in enumerate(profiles):
                print(f"\t\033[36m{i+1}. {profile.name}\033[0m")
            
            profile_index, cancelled = validate_int("profile number to delete", 1, len(profiles))
            if cancelled:
                continue
            profile_index -= 1
            selected_profile = profiles[profile_index]
            
            # Confirm deletion
            try:
                confirmation = input(f"\tAre you sure you want to delete profile '{selected_profile.name}'? This will also delete all computers using this profile. (y/N): ")
            except KeyboardInterrupt:
                print("\n\t\033[36mDeletion cancelled.\033[0m")
                continue
            if confirmation.lower() == 'y':
                status, message, _ = delete_profile(selected_profile.name)
                if status:
                    print(f"\t\033[94m{message}\033[0m")
                else:
                    print(f"\t\033[31m{message}\033[0m")
            else:
                print("\t\033[36mDeletion cancelled.\033[0m")
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Run 'help' for profile instructions.\033[0m")



if __name__ == "__main__":
    status, message, error_code = create_profile(name="Developer")
    print(status, message, error_code)
    status, message, error_code = create_profile(name="Producer")
    print(status, message, error_code)
    status, message, error_code = add_step_to_profile(profile_name="Producer", step_name="Change computer font")
    print(status, message, error_code)
