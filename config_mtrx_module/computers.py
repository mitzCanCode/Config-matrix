### Custom module imports:
from .db import Computers, SetupSteps, Technicians, ComputerAttributes, get_db_session
from .utils import StatusCodes
from datetime import datetime

def get_computer_by(computer_name: str = '', computer_technician: str = '') -> tuple:
    with get_db_session() as session:
        if computer_name:
            computer = session.query(Computers).filter_by(name=computer_name).first()
        elif computer_technician:
            computer = session.query(Computers).filter_by(name=computer_name).first()
        else:
            return (False, f"No filter form specified", None, StatusCodes.bad_request)
        
        if not computer:
                return (False, f"Computer '{computer_name}' not found", None, StatusCodes.not_found)
        else:
            return (True, f"Computer '{computer_name}' found", computer, StatusCodes.success)
    
def get_computer_assigned_technician(computer_name: str) -> tuple:
    try:
        # Computer fetching
        computer_response = get_computer_by(computer_name=computer_name)
        if not computer_response[0]: # Handle computer fetching error
            return computer_response
        computer = computer_response[2] # Get computer element from response
        
        if not computer.technician_id:
            return (True, f"No technician assigned to '{computer_name}'", None, StatusCodes.success)
                
        # Respond accordingly to technician existing or not
        if computer.technician:
            return (True, f"Technician '{computer.technician.name}' is assigned to '{computer_name}'", computer.technician, StatusCodes.success)
        else:
            return (False, f"Technician data not found for computer '{computer_name}'", None, StatusCodes.not_found)
    
    except Exception as e:
        print(e)
        return (False, "Error retrieving assigned technician", None, StatusCodes.internal_server_error)

def get_computer_deadline(computer_name: str) -> tuple:
    try:
        # Computer fetching
        computer_response = get_computer_by(computer_name=computer_name) 
        if not computer_response[0]: # Handle computer fetching error
            return computer_response
        computer = computer_response[2] # Get computer element from response
        
        if computer.deadline:
            return (True, f"Computer '{computer_name}' has a deadline on {computer.deadline}", computer.deadline, StatusCodes.success)
        else:
            return (True, f"No deadline set for '{computer_name}'", None, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, "Error retrieving computer deadline", None, StatusCodes.internal_server_error)

def toggle_step(computer_name: str, step_name: str) -> tuple: 
    try:
        with get_db_session() as session:
            # Finding computer 
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Finding step
            step = session.query(SetupSteps).filter_by(name=step_name).first()
            if not step:
                return (False, f"Setup step '{step_name}' not found", StatusCodes.not_found)
            
            if step in computer.setup_steps: # Remove existing step
                computer.setup_steps.remove(step)
                return (True, f"Step '{step_name}' removed from: '{computer_name}'", StatusCodes.success)
            else: # Add existing step
                computer.setup_steps.append(step) 
                return (True, f"Marked step '{step_name}' as complete for '{computer_name}'", StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error changing step value", StatusCodes.internal_server_error)

def retrieve_all_computers() -> tuple:
    try: 
        with get_db_session() as session:
            # Retrieving all computers
            computers = session.query(Computers).all()
            if computers:
                serialized_computers = [
                    {
                        'id': computer.id,
                        'name': computer.name,
                        'profile_id': computer.profile_id,
                        'deadline': computer.deadline.isoformat() if computer.deadline else None, # type: ignore
                        'notes': computer.notes,
                        'setup_steps': [step.id for step in computer.setup_steps],  # Serialize related setup steps
                        'technicians': [{'id': tech.id, 'name': tech.name} for tech in computer.technicians],  # Serialize related technicians with names
                        'attributes': {attr.key: attr.value for attr in computer.attributes}  # Serialize custom attributes
                    }
                    for computer in computers
                ]
                return (True, "Computers retrieved successfully", serialized_computers, StatusCodes.success)
            else:
                return (True, "No computers have been created yet", [], StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "An error occurred while mapping computers", [], StatusCodes.internal_server_error)

def edit_computer_name(current_name: str, new_name: str) -> tuple:
    try:
        with get_db_session() as session:
            # Find the computer by current name
            computer = session.query(Computers).filter_by(name=current_name).first()
            if not computer: # Handle computer not existing
                return (False, f"Computer '{current_name}' not found", StatusCodes.not_found)
            
            
            existing = session.query(Computers).filter_by(name=new_name).first()
            # Check if new name already exists and if another computer is the one that has it
            if existing and existing.id != computer.id: # type: ignore
                return (False, f"Computer name '{new_name}' already exists", 409)
            
            # Update the name
            computer.name = new_name  # type: ignore
            
            return (True, f"Computer name changed from '{current_name}' to '{new_name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating computer name", StatusCodes.internal_server_error)

def edit_computer_deadline(computer_name: str, new_deadline: datetime) -> tuple:
    try:
        with get_db_session() as session:
            # Find the computer by name
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer: # Handle computer not existing
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Store old deadline for confirmation message
            old_deadline = computer.deadline
            
            # Update the deadline
            computer.deadline = new_deadline # type: ignore
            
            return (True, f"Computer '{computer_name}' deadline changed from {old_deadline} to {new_deadline}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating computer deadline", StatusCodes.internal_server_error)

def get_computer_progress(computer_name: str) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer: # Handle computer not existing
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)

            completed_steps = computer.setup_steps
            profile = computer.profile

            if not profile:
                return (False, f"No profile associated with '{computer_name}'", StatusCodes.not_found)

            total_steps = profile.setup_steps_to_follow
            remaining_steps = [step for step in total_steps if step not in completed_steps]

            # Serialize the steps data to prevent session binding issues
            completed_steps_data = [
                {
                    "id": step.id,
                    "name": step.name,
                    "download_link": step.download_link
                }
                for step in completed_steps
            ]
            
            remaining_steps_data = [
                {
                    "id": step.id,
                    "name": step.name,
                    "download_link": step.download_link
                }
                for step in remaining_steps
            ]

            return (True, {
                "completed_steps": completed_steps_data,
                "remaining_steps": remaining_steps_data
            }, StatusCodes.success)

    except Exception as e:
        print(e)
        return (False, "Error retrieving computer progress", StatusCodes.internal_server_error)

def get_computer_progress_by_id(computer_id: int) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer: # Handle computer not existing
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)

            completed_steps = computer.setup_steps
            profile = computer.profile

            if not profile:
                return (False, f"No profile associated with computer ID '{computer_id}'", StatusCodes.not_found)

            total_steps = profile.setup_steps_to_follow
            remaining_steps = [step for step in total_steps if step not in completed_steps]

            # Serialize the steps data to prevent session binding issues
            completed_steps_data = [
                {
                    "id": step.id,
                    "name": step.name,
                    "download_link": step.download_link
                }
                for step in completed_steps
            ]
            
            remaining_steps_data = [
                {
                    "id": step.id,
                    "name": step.name,
                    "download_link": step.download_link
                }
                for step in remaining_steps
            ]

            return (True, {
                "completed_steps": completed_steps_data,
                "remaining_steps": remaining_steps_data
            }, StatusCodes.success)

    except Exception as e:
        print(e)
        return (False, "Error retrieving computer progress", StatusCodes.internal_server_error)

def create_computer(name: str, deadline: datetime, profile_id: int, technician_ids: list) -> tuple:
    try:
        with get_db_session() as session:
            # Check if computer exists
            computer = session.query(Computers).filter_by(name=name).first()
            if computer:
                return (False, f"Computer '{name}' already exists", 409)
            
            # Verify technicians exist
            technicians = session.query(Technicians).filter(Technicians.id.in_(technician_ids)).all()
            if not technicians or len(technicians) != len(technician_ids):
                return (False, "Some technician IDs are invalid", StatusCodes.not_found)
            
            # Check if profile exists
            from .db import Profiles
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            if not profile:
                return (False, f"Profile with ID {profile_id} not found", StatusCodes.not_found)

            new_computer = Computers(
                name = name,
                deadline = deadline,
                profile_id = profile_id,
                setup_steps = []
            )

            # Assign technicians
            new_computer.technicians.extend(technicians)

            # Create computer first
            session.add(new_computer)
            session.flush()  # Ensure computer ID is available
            
            # Auto-assign preset attributes from profile to computer
            profile_attributes = profile.preset_attributes
            for preset_attr in profile_attributes:
                new_attr = ComputerAttributes(
                    computer_id=new_computer.id,
                    key=preset_attr.key,
                    value=preset_attr.value
                )
                session.add(new_attr)
            
            technicians_names_lst = [tech.name for tech in technicians]
            technician_names = ', '.join(technicians_names_lst) # type: ignore
            
            # Add message about auto-assigned attributes
            message = f"Computer ({name}) was created and assigned to technicians: {technician_names}"
            if profile_attributes:
                attr_keys = [attr.key for attr in profile_attributes]
                message += f". Auto-assigned preset attributes: {', '.join(attr_keys)}"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Computer ({name}) creation failed", StatusCodes.internal_server_error)

def assign_technicians_to_computer(computer_name: str, technician_ids: list) -> tuple:
    """Assign multiple technicians to a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            technicians = session.query(Technicians).filter(Technicians.id.in_(technician_ids)).all()
            if not technicians:
                return (False, "No valid technicians found", StatusCodes.not_found)
            
            # Clear existing assigned technicians
            computer.technicians = []

            # Assign the technicians
            computer.technicians.extend(technicians)
                        
            technician_names = ', '.join([t.name for t in technicians]) # type: ignore
            return (True, f"Computer '{computer_name}' now assigned to technicians: {technician_names}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, "Error assigning technicians to computer", StatusCodes.internal_server_error)

def assign_profile_to_computer(computer_name: str, profile_id: int) -> tuple:
    """Assign a profile to a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Check if profile exists
            from .db import Profiles
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            if not profile:
                return (False, f"Profile with ID {profile_id} not found", StatusCodes.not_found)
            
            # Check if computer already has this profile assigned
            if computer.profile_id == profile_id: # type: ignore
                return (False, f"Computer '{computer_name}' already has profile '{profile.name}' assigned", 409)
            
            # Store old profile name for confirmation message
            old_profile_name = computer.profile.name if computer.profile else "No profile"
            
            # Assign the profile
            computer.profile_id = profile_id # type: ignore
            
            # Clear completed steps since profile changed
            computer.setup_steps = [] # type: ignore
            
            # Clear existing attributes and assign new preset attributes from profile
            # First, remove all existing attributes
            session.query(ComputerAttributes).filter_by(computer_id=computer.id).delete()
            
            # Then add the new preset attributes from the profile
            profile_attributes = profile.preset_attributes
            for preset_attr in profile_attributes:
                new_attr = ComputerAttributes(
                    computer_id=computer.id,
                    key=preset_attr.key,
                    value=preset_attr.value
                )
                session.add(new_attr)
            
            # Build message
            message = f"Computer '{computer_name}' profile changed from '{old_profile_name}' to '{profile.name}'. Setup steps have been reset."
            if profile_attributes:
                attr_keys = [attr.key for attr in profile_attributes]
                message += f" Preset attributes applied: {', '.join(attr_keys)}"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error assigning profile to computer", StatusCodes.internal_server_error)

def delete_computer(computer_name: str) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Store computer name for confirmation message
            name = computer.name
            
            # Delete the computer (setup steps will be automatically removed due to relationship)
            session.delete(computer)
            
            return (True, f"Computer '{name}' has been deleted successfully", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error deleting computer '{computer_name}'", StatusCodes.internal_server_error)

def edit_computer_notes(computer_name: str, notes: str) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Update the notes
            computer.notes = notes  # type: ignore            
            return (True, f"Notes updated for computer '{computer_name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating notes for computer '{computer_name}'", StatusCodes.internal_server_error)


def calculate_progress(computer):
    """Calculate progress information for a computer"""
    try:
        completed_steps = computer.setup_steps
        profile = computer.profile
        
        if not profile:
            return {
                "completed_steps_num": 0,
                "remaining_steps_num": 0,
                "total_step_num": 0,
                "completed_steps": [],
                "remaining_steps": []
            }
        
        total_steps = profile.setup_steps_to_follow
        remaining_steps = [step for step in total_steps if step not in completed_steps]
        
        return {
            "completed_steps_num": len(completed_steps),
            "remaining_steps_num": len(remaining_steps),
            "total_step_num": len(remaining_steps) + len(completed_steps),
            "completed_steps": [step.name for step in completed_steps],
            "remaining_steps": [step.name for step in remaining_steps]
        }
    except Exception as e:
        print(f"Error calculating progress: {e}")
        return {
            "completed_steps_num": 0,
            "remaining_steps_num": 0,
            "total_step_num": 0,
            "completed_steps": [],
            "remaining_steps": []
        }

def computer_info(computer_name: str) -> dict:
    with get_db_session() as session:
        computer = session.query(Computers).filter_by(name=computer_name).first()
        if not computer:
            return {"Error": f"Computer '{computer_name}' not found", "code": 404}
        
        # Get custom attributes
        attributes = {attr.key: attr.value for attr in computer.attributes}
        
        return {
            "id": computer.id,
            "name": computer.name,
            "profile": {"name": computer.profile.name, "id": computer.profile.id} if computer.profile else None,
            "technicians": [{"name": t.name, "id": t.id} for t in computer.technicians],
            "deadline": computer.deadline.strftime("%Y-%m-%d %H:%M:%S") if computer.deadline else None, # type: ignore
            "notes": computer.notes or "",
            "attributes": attributes,
            **calculate_progress(computer)
        }

def computer_info_by_id(computer_id: int) -> dict:
    with get_db_session() as session:
        computer = session.query(Computers).filter_by(id=computer_id).first()
        if not computer:
            return {"Error": f"Computer with ID '{computer_id}' not found", "code": 404}
        
        # Get custom attributes
        attributes = {attr.key: attr.value for attr in computer.attributes}
        
        return {
            "id": computer.id,
            "name": computer.name,
            "profile": {"name": computer.profile.name, "id": computer.profile.id} if computer.profile else None,
            "technicians": [{"name": t.name, "id": t.id} for t in computer.technicians],
            "deadline": computer.deadline.strftime("%Y-%m-%d %H:%M:%S") if computer.deadline else None, # type: ignore
            "notes": computer.notes or "",
            "attributes": attributes,
            **calculate_progress(computer)
        }

def set_computer_attribute(computer_name: str, key: str, value: str) -> tuple:
    """Set a custom attribute for a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Check if attribute already exists
            existing_attr = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if existing_attr:
                # Update existing attribute
                old_value = existing_attr.value
                existing_attr.value = value
                return (True, f"Attribute '{key}' updated for computer '{computer_name}' from '{old_value}' to '{value}'", StatusCodes.success)
            else:
                # Create new attribute
                new_attr = ComputerAttributes(
                    computer_id=computer.id,
                    key=key,
                    value=value
                )
                session.add(new_attr)
                return (True, f"Attribute '{key}' set to '{value}' for computer '{computer_name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attribute for computer '{computer_name}'", StatusCodes.internal_server_error)

def get_computer_attribute(computer_name: str, key: str) -> tuple:
    """Get a specific custom attribute for a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", None, StatusCodes.not_found)
            
            attribute = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if attribute:
                return (True, f"Attribute '{key}' found for computer '{computer_name}'", attribute.value, StatusCodes.success)
            else:
                return (True, f"Attribute '{key}' not found for computer '{computer_name}'", None, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attribute for computer '{computer_name}'", None, StatusCodes.internal_server_error)

def get_computer_attributes(computer_name: str) -> tuple:
    """Get all custom attributes for a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", None, StatusCodes.not_found)
            
            attributes = {attr.key: attr.value for attr in computer.attributes}
            return (True, f"Attributes retrieved for computer '{computer_name}'", attributes, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attributes for computer '{computer_name}'", None, StatusCodes.internal_server_error)

def delete_computer_attribute(computer_name: str, key: str) -> tuple:
    """Delete a custom attribute for a computer"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            attribute = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if attribute:
                session.delete(attribute)
                return (True, f"Attribute '{key}' deleted from computer '{computer_name}'", StatusCodes.success)
            else:
                return (False, f"Attribute '{key}' not found for computer '{computer_name}'", StatusCodes.not_found)
    
    except Exception as e:
        print(e)
        return (False, f"Error deleting attribute for computer '{computer_name}'", StatusCodes.internal_server_error)

def set_computer_attributes(computer_name: str, attributes: dict) -> tuple:
    """Set multiple custom attributes for a computer (replaces all existing attributes)"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(name=computer_name).first()
            if not computer:
                return (False, f"Computer '{computer_name}' not found", StatusCodes.not_found)
            
            # Get all existing attributes for this computer
            existing_attrs = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id
            ).all()
            
            # Create sets of keys for comparison
            existing_keys = {attr.key for attr in existing_attrs}
            new_keys = set(attributes.keys())
            
            updated_attrs = []
            created_attrs = []
            deleted_attrs = []
            
            # Update or create attributes
            for key, value in attributes.items():
                existing_attr = session.query(ComputerAttributes).filter_by(
                    computer_id=computer.id, key=key
                ).first()
                
                if existing_attr:
                    # Update existing attribute
                    existing_attr.value = value
                    updated_attrs.append(key)
                else:
                    # Create new attribute
                    new_attr = ComputerAttributes(
                        computer_id=computer.id,
                        key=key,
                        value=value
                    )
                    session.add(new_attr)
                    created_attrs.append(key)
            
            # Delete attributes that are no longer present
            keys_to_delete = existing_keys - new_keys
            for key in keys_to_delete:
                attr_to_delete = session.query(ComputerAttributes).filter_by(
                    computer_id=computer.id, key=key
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
                message = f"Attributes set for computer '{computer_name}'. " + "; ".join(message_parts)
            else:
                message = f"No changes made to attributes for computer '{computer_name}'"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attributes for computer '{computer_name}'", StatusCodes.internal_server_error)

# ID-based versions of computer functions
def toggle_step_by_id(computer_id: int, step_name: str) -> tuple:
    try:
        with get_db_session() as session:
            # Finding computer by ID
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Finding step
            step = session.query(SetupSteps).filter_by(name=step_name).first()
            if not step:
                return (False, f"Setup step '{step_name}' not found", StatusCodes.not_found)
            
            if step in computer.setup_steps: # Remove existing step
                computer.setup_steps.remove(step)
                return (True, f"Step '{step_name}' removed from computer '{computer.name}'", StatusCodes.success)
            else: # Add existing step
                computer.setup_steps.append(step)
                return (True, f"Marked step '{step_name}' as complete for computer '{computer.name}'", StatusCodes.success)
    except Exception as e:
        print(e)
        return (False, "Error changing step value", StatusCodes.internal_server_error)

def edit_computer_name_by_id(computer_id: int, new_name: str) -> tuple:
    try:
        with get_db_session() as session:
            # Find the computer by ID
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Store old name for confirmation message
            old_name = computer.name
            
            # Check if new name already exists
            existing = session.query(Computers).filter_by(name=new_name).first()
            if existing and existing.id != computer.id:
                return (False, f"Computer name '{new_name}' already exists", 409)
            
            # Update the name
            computer.name = new_name
            
            return (True, f"Computer name changed from '{old_name}' to '{new_name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating computer name", StatusCodes.internal_server_error)

def edit_computer_deadline_by_id(computer_id: int, new_deadline: datetime) -> tuple:
    try:
        with get_db_session() as session:
            # Find the computer by ID
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Store old deadline for confirmation message
            old_deadline = computer.deadline
            
            # Update the deadline
            computer.deadline = new_deadline
            
            return (True, f"Computer '{computer.name}' deadline changed from {old_deadline} to {new_deadline}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating computer deadline", StatusCodes.internal_server_error)

def edit_computer_notes_by_id(computer_id: int, notes: str) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Update the notes
            computer.notes = notes
            return (True, f"Notes updated for computer '{computer.name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error updating notes for computer", StatusCodes.internal_server_error)

def assign_technicians_to_computer_by_id(computer_id: int, technician_ids: list) -> tuple:
    """Assign multiple technicians to a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            technicians = session.query(Technicians).filter(Technicians.id.in_(technician_ids)).all()
            if not technicians:
                return (False, "No valid technicians found", StatusCodes.not_found)
            
            # Clear existing assigned technicians
            computer.technicians = []
            
            # Assign the technicians
            computer.technicians.extend(technicians)
            
            technician_names = ', '.join([t.name for t in technicians])
            return (True, f"Computer '{computer.name}' now assigned to technicians: {technician_names}", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, "Error assigning technicians to computer", StatusCodes.internal_server_error)

def assign_profile_to_computer_by_id(computer_id: int, profile_id: int) -> tuple:
    """Assign a profile to a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Check if profile exists
            from .db import Profiles
            profile = session.query(Profiles).filter_by(id=profile_id).first()
            if not profile:
                return (False, f"Profile with ID {profile_id} not found", StatusCodes.not_found)
            
            # Check if computer already has this profile assigned
            if computer.profile_id == profile_id:
                return (False, f"Computer '{computer.name}' already has profile '{profile.name}' assigned", 409)
            
            # Store old profile name for confirmation message
            old_profile_name = computer.profile.name if computer.profile else "No profile"
            
            # Assign the profile
            computer.profile_id = profile_id
            
            # Clear completed steps since profile changed
            computer.setup_steps = []
            
            # Clear existing attributes and assign new preset attributes from profile
            # First, remove all existing attributes
            session.query(ComputerAttributes).filter_by(computer_id=computer.id).delete()
            
            # Then add the new preset attributes from the profile
            profile_attributes = profile.preset_attributes
            for preset_attr in profile_attributes:
                new_attr = ComputerAttributes(
                    computer_id=computer.id,
                    key=preset_attr.key,
                    value=preset_attr.value
                )
                session.add(new_attr)
            
            # Build message
            message = f"Computer '{computer.name}' profile changed from '{old_profile_name}' to '{profile.name}'. Setup steps have been reset."
            if profile_attributes:
                attr_keys = [attr.key for attr in profile_attributes]
                message += f" Preset attributes applied: {', '.join(attr_keys)}"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error assigning profile to computer", StatusCodes.internal_server_error)

def delete_computer_by_id(computer_id: int) -> tuple:
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Store computer name for confirmation message
            name = computer.name
            
            # Delete the computer
            session.delete(computer)
            
            return (True, f"Computer '{name}' has been deleted successfully", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error deleting computer", StatusCodes.internal_server_error)

def set_computer_attribute_by_id(computer_id: int, key: str, value: str) -> tuple:
    """Set a custom attribute for a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Check if attribute already exists
            existing_attr = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if existing_attr:
                # Update existing attribute
                old_value = existing_attr.value
                existing_attr.value = value
                return (True, f"Attribute '{key}' updated for computer '{computer.name}' from '{old_value}' to '{value}'", StatusCodes.success)
            else:
                # Create new attribute
                new_attr = ComputerAttributes(
                    computer_id=computer.id,
                    key=key,
                    value=value
                )
                session.add(new_attr)
                return (True, f"Attribute '{key}' set to '{value}' for computer '{computer.name}'", StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attribute for computer", StatusCodes.internal_server_error)

def get_computer_attribute_by_id(computer_id: int, key: str) -> tuple:
    """Get a specific custom attribute for a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", None, StatusCodes.not_found)
            
            attribute = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if attribute:
                return (True, f"Attribute '{key}' found for computer '{computer.name}'", attribute.value, StatusCodes.success)
            else:
                return (True, f"Attribute '{key}' not found for computer '{computer.name}'", None, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attribute for computer", None, StatusCodes.internal_server_error)

def get_computer_attributes_by_id(computer_id: int) -> tuple:
    """Get all custom attributes for a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", None, StatusCodes.not_found)
            
            attributes = {attr.key: attr.value for attr in computer.attributes}
            return (True, f"Attributes retrieved for computer '{computer.name}'", attributes, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error retrieving attributes for computer", None, StatusCodes.internal_server_error)

def delete_computer_attribute_by_id(computer_id: int, key: str) -> tuple:
    """Delete a custom attribute for a computer by ID"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            attribute = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id, key=key
            ).first()
            
            if attribute:
                session.delete(attribute)
                return (True, f"Attribute '{key}' deleted from computer '{computer.name}'", StatusCodes.success)
            else:
                return (False, f"Attribute '{key}' not found for computer '{computer.name}'", StatusCodes.not_found)
    
    except Exception as e:
        print(e)
        return (False, f"Error deleting attribute for computer", StatusCodes.internal_server_error)

def set_computer_attributes_by_id(computer_id: int, attributes: dict) -> tuple:
    """Set multiple custom attributes for a computer by ID (replaces all existing attributes)"""
    try:
        with get_db_session() as session:
            computer = session.query(Computers).filter_by(id=computer_id).first()
            if not computer:
                return (False, f"Computer with ID '{computer_id}' not found", StatusCodes.not_found)
            
            # Get all existing attributes for this computer
            existing_attrs = session.query(ComputerAttributes).filter_by(
                computer_id=computer.id
            ).all()
            
            # Create sets of keys for comparison
            existing_keys = {attr.key for attr in existing_attrs}
            new_keys = set(attributes.keys())
            
            updated_attrs = []
            created_attrs = []
            deleted_attrs = []
            
            # Update or create attributes
            for key, value in attributes.items():
                existing_attr = session.query(ComputerAttributes).filter_by(
                    computer_id=computer.id, key=key
                ).first()
                
                if existing_attr:
                    # Update existing attribute
                    existing_attr.value = value
                    updated_attrs.append(key)
                else:
                    # Create new attribute
                    new_attr = ComputerAttributes(
                        computer_id=computer.id,
                        key=key,
                        value=value
                    )
                    session.add(new_attr)
                    created_attrs.append(key)
            
            # Delete attributes that are no longer present
            keys_to_delete = existing_keys - new_keys
            for key in keys_to_delete:
                attr_to_delete = session.query(ComputerAttributes).filter_by(
                    computer_id=computer.id, key=key
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
                message = f"Attributes set for computer '{computer.name}'. " + "; ".join(message_parts)
            else:
                message = f"No changes made to attributes for computer '{computer.name}'"
            
            return (True, message, StatusCodes.success)
    
    except Exception as e:
        print(e)
        return (False, f"Error setting attributes for computer", StatusCodes.internal_server_error)
