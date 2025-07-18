### Custom module imports:
from .db import get_db_session, Profiles, SetupSteps, Computers, ProfileAttributes
from .utils import StatusCodes
from .steps import retrieve_all_steps

def add_step_to_profile(profile_name: str, step_name: str) -> tuple:
    with get_db_session() as session:
        step = session.query(SetupSteps).filter_by(name=step_name).first() # Find step
        
        if not step: # Handle step not existing
            return (False, "Setup step not found", StatusCodes.not_found)
        
        profile = session.query(Profiles).filter_by(name=profile_name).first() # Find profile
        
        if not profile: # Handle profile not existing
            return (False, "Profile not found", StatusCodes.not_found)
        
        profile.setup_steps_to_follow.append(step) # Add step to profile
        return (True, f"Added {step.name} to profile {profile.name}", StatusCodes.success)

def create_profile(name: str) -> tuple:
    try:
        with get_db_session() as session:
            existing = session.query(Profiles).filter_by(name=name).first()
            if existing:
                return (False, f"Profile '{name}' already exists", 409)
            
            new_profile = Profiles(
                name = name,
            )
            session.add(new_profile)
            return (True, f"Profile '{name}' created successfully", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"An error occured trying to create '{name}' profile", StatusCodes.internal_server_error)

def delete_profile(name: str) -> tuple:
    try:
        with get_db_session() as session:
            # Fetch the profile
            profile = session.query(Profiles).filter_by(name=name).first()
            if not profile:
                return (False, f"Profile '{name}' not found", StatusCodes.not_found)

            # Delete all computers using this profile
            session.query(Computers).filter_by(profile_id=profile.id).delete()

            # Delete the profile itself
            session.delete(profile)

            return (True, f"Profile '{name}' and its computers deleted", StatusCodes.success)

    except Exception as e:
        print(e)
        return (False, f"Error deleting profile '{name}'", StatusCodes.internal_server_error)
    
def retrieve_all_profiles() -> tuple:
    try: 
        with get_db_session() as session:
            # Retrieving all profiles
            profiles = session.query(Profiles).all()
            
            if profiles:
                serialized_profiles = [
                   {
                       'id': profile.id,
                       'name': profile.name,
                   }
                   for profile in profiles
                ]
                return (True, "Profiles retrieved successfully", serialized_profiles, StatusCodes.success)
            else:
                return (True, "No profiles have been created yet", [], StatusCodes.success)
    except Exception as e:
        return (False, "An error occurred while mapping profiles", [], StatusCodes.internal_server_error)

def get_profile_steps(profile_name: str) -> tuple:
    try:        
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", [], StatusCodes.not_found)
            
            steps = profile.setup_steps_to_follow
            serialized_steps = [
                {
                    'id': step.id,
                    'name': step.name,
                    'download_link': step.download_link or ""
                }
                for step in steps
            ]
            return (True, f"Steps for profile '{profile_name}'", serialized_steps, StatusCodes.success)
    except Exception as e:
        return (False, "An error occurred while retrieving profile steps", [], StatusCodes.internal_server_error)

def remove_step_from_profile(profile_name: str, step_name: str) -> tuple:
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(name=step_name).first()
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            
            if not step:
                return (False, "Setup step not found", StatusCodes.not_found)
            if not profile:
                return (False, "Profile not found", StatusCodes.not_found)
            
            # Check if step is actually assigned to the profile
            if step not in profile.setup_steps_to_follow:
                return (False, f"Step '{step_name}' is not assigned to profile '{profile_name}'", StatusCodes.not_found)
            
            # Remove the step from the profile
            profile.setup_steps_to_follow.remove(step)
            return (True, f"Removed {step.name} from profile {profile.name}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error removing step from profile", StatusCodes.internal_server_error)

def get_available_steps_for_profile(profile_id: int) -> tuple:
    """Get all steps that are not currently assigned to a profile"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            if not profile:
                return (False, "Profile not found", [], StatusCodes.not_found)
            
            # Get all steps
            all_steps = session.query(SetupSteps).all()
            
            # Get steps already assigned to this profile - access within session
            assigned_steps = profile.setup_steps_to_follow
            assigned_step_ids = [step.id for step in assigned_steps]
            
            # Filter out already assigned steps and create new list with data
            available_steps = []
            for step in all_steps:
                if step.id not in assigned_step_ids:
                    # Create a new object with the data we need
                    available_steps.append({
                        'id': step.id,
                        'name': step.name,
                        'download_link': step.download_link or ""
                    })
            
            return (True, "Available steps retrieved", available_steps, StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error retrieving available steps", [], StatusCodes.internal_server_error)

def remove_step_from_profile_by_id(profile_id: int, step_id: int) -> tuple:
    """Remove a step from a profile by their IDs"""
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(id=step_id).first()
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            
            if not step:
                return (False, "Setup step not found", StatusCodes.not_found)
            if not profile:
                return (False, "Profile not found", StatusCodes.not_found)
            
            # Check if step is actually assigned to the profile
            if step not in profile.setup_steps_to_follow:
                return (False, f"Step '{step.name}' is not assigned to this profile", StatusCodes.not_found)
            
            # Remove the step from the profile
            profile.setup_steps_to_follow.remove(step)
            return (True, f"Removed {step.name} from profile {profile.name}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error removing step from profile", StatusCodes.internal_server_error)

def add_step_to_profile_by_id(profile_id: int, step_id: int) -> tuple:
    """Add a step to a profile by their IDs"""
    try:
        with get_db_session() as session:
            step = session.query(SetupSteps).filter_by(id=step_id).first()
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            
            if not step:
                return (False, "Setup step not found", StatusCodes.not_found)
            if not profile:
                return (False, "Profile not found", StatusCodes.not_found)
            
            # Check if step is already assigned to the profile
            if step in profile.setup_steps_to_follow:
                return (False, f"Step '{step.name}' is already assigned to this profile", StatusCodes.conflict)
            
            # Add the step to the profile
            profile.setup_steps_to_follow.append(step)
            return (True, f"Added {step.name} to profile {profile.name}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error adding step to profile", StatusCodes.internal_server_error)

def set_profile_attribute(profile_name: str, key: str, value: str) -> tuple:
    """Set a preset attribute for a profile"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", StatusCodes.not_found)
            
            # Check if attribute already exists
            existing_attr = session.query(ProfileAttributes).filter_by(
                profile_id=profile.id, key=key
            ).first()
            
            if existing_attr:
                # Update existing attribute
                old_value = existing_attr.value
                existing_attr.value = value
                return (True, f"Attribute '{key}' updated for profile '{profile_name}' from '{old_value}' to '{value}'", StatusCodes.success)
            else:
                # Create new attribute
                new_attr = ProfileAttributes(
                    profile_id=profile.id,
                    key=key,
                    value=value
                )
                session.add(new_attr)
                return (True, f"Attribute '{key}' set to '{value}' for profile '{profile_name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attribute for profile '{profile_name}'", StatusCodes.internal_server_error)

def get_profile_attribute(profile_name: str, key: str) -> tuple:
    """Get a specific preset attribute for a profile"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", None, StatusCodes.not_found)
            
            attribute = session.query(ProfileAttributes).filter_by(
                profile_id=profile.id, key=key
            ).first()
            
            if attribute:
                return (True, f"Attribute '{key}' found for profile '{profile_name}'", attribute.value, StatusCodes.success)
            else:
                return (True, f"Attribute '{key}' not found for profile '{profile_name}'", None, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attribute for profile '{profile_name}'", None, StatusCodes.internal_server_error)

def get_profile_attributes(profile_name: str) -> tuple:
    """Get all preset attributes for a profile"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", None, StatusCodes.not_found)
            
            attributes = {attr.key: attr.value for attr in profile.preset_attributes}
            return (True, f"Attributes retrieved for profile '{profile_name}'", attributes, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attributes for profile '{profile_name}'", None, StatusCodes.internal_server_error)

def delete_profile_attribute(profile_name: str, key: str) -> tuple:
    """Delete a preset attribute for a profile"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", StatusCodes.not_found)
            
            attribute = session.query(ProfileAttributes).filter_by(
                profile_id=profile.id, key=key
            ).first()
            
            if attribute:
                session.delete(attribute)
                return (True, f"Attribute '{key}' deleted from profile '{profile_name}'", StatusCodes.success)
            else:
                return (False, f"Attribute '{key}' not found for profile '{profile_name}'", StatusCodes.not_found)
    
    except Exception as e:
        print(e)
        return (False, f"Error deleting attribute for profile '{profile_name}'", StatusCodes.internal_server_error)

def set_profile_attributes(profile_name: str, attributes: dict) -> tuple:
    """Set multiple preset attributes for a profile (replaces all existing attributes)"""
    try:
        with get_db_session() as session:
            profile = session.query(Profiles).filter_by(name=profile_name).first()
            if not profile:
                return (False, f"Profile '{profile_name}' not found", StatusCodes.not_found)
            
            # Get all existing attributes for this profile
            existing_attrs = session.query(ProfileAttributes).filter_by(
                profile_id=profile.id
            ).all()
            
            # Create sets of keys for comparison
            existing_keys = {attr.key for attr in existing_attrs}
            new_keys = set(attributes.keys())
            
            updated_attrs = []
            created_attrs = []
            deleted_attrs = []
            
            # Update or create attributes
            for key, value in attributes.items():
                existing_attr = session.query(ProfileAttributes).filter_by(
                    profile_id=profile.id, key=key
                ).first()
                
                if existing_attr:
                    # Update existing attribute
                    existing_attr.value = value
                    updated_attrs.append(key)
                else:
                    # Create new attribute
                    new_attr = ProfileAttributes(
                        profile_id=profile.id,
                        key=key,
                        value=value
                    )
                    session.add(new_attr)
                    created_attrs.append(key)
            
            # Delete attributes that are no longer present
            keys_to_delete = existing_keys - new_keys
            for key in keys_to_delete:
                attr_to_delete = session.query(ProfileAttributes).filter_by(
                    profile_id=profile.id, key=key
                ).first()
                if attr_to_delete:
                    session.delete(attr_to_delete)
                    deleted_attrs.append(key)
            
            # Build message
            message_parts = []
            if created_attrs:
                message_parts.append(f"Created attributes: {', '.join(created_attrs)}")
            if updated_attrs:
                message_parts.append(f"Updated attributes: {', '.join(updated_attrs)}")
            if deleted_attrs:
                message_parts.append(f"Deleted attributes: {', '.join(deleted_attrs)}")
            
            if message_parts:
                message = f"Attributes set for profile '{profile_name}'. " + "; ".join(message_parts)
            else:
                message = f"No changes made to attributes for profile '{profile_name}'"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attributes for profile '{profile_name}'", StatusCodes.internal_server_error)
