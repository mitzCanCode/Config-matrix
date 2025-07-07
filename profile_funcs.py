from db import session, Profiles, Apps, Computers

def add_app_to_profile(profile_name: str, app_name: str) -> tuple:
    app = session.query(Apps).filter_by(name=app_name).first()
    profile = session.query(Profiles).filter_by(name=profile_name).first()
    if not app:
        return (False, "App not found", 404)
    if not profile:
        return (False, "Profile not found", 404)
    
    profile.apps_to_download.append(app)
    session.commit()
    return (True, f"Added {app.name} to profile {profile.name}", 200)

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
        # Retrieving all apps
        profiles = session.query(Profiles).all()
        
        if profiles:
            return (True, "Apps retrieved successfully", profiles, 200)
        else:
            return (True, "No apps have been created yet", profiles, 200)
    except Exception as e:
        return (False, "An error occured while mapping apps", [],500)

if __name__ == "__main__":
    status, message, error_code = create_profile(name="Developer")
    print(status, message, error_code)
    status, message, error_code = create_profile(name="Producer")
    print(status, message, error_code)
    status, message, error_code = add_app_to_profile(profile_name="Producer", app_name="Apple music")
    print(status, message, error_code)