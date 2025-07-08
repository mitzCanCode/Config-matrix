from db import session, Profiles, SetupSteps, Computers

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

if __name__ == "__main__":
    status, message, error_code = create_profile(name="Developer")
    print(status, message, error_code)
    status, message, error_code = create_profile(name="Producer")
    print(status, message, error_code)
    status, message, error_code = add_step_to_profile(profile_name="Producer", step_name="Change computer font")
    print(status, message, error_code)
