from profile_funcs import create_profile, retrieve_all_profiles, add_step_to_profile, get_profile_steps, remove_step_from_profile, delete_profile
from step_funcs import create_step, retrieve_all_steps, delete_step
from computer_funcs import create_computer, retrieve_all_computers, edit_computer_name, edit_computer_deadline, mark_step_complete, mark_step_incomplete, get_computer_progress, get_remaining_steps
from db import session, Computers
from datetime import datetime
import time
import sys


config_text = r"""                             .-') _                                
                            ( OO ) )                               
   .-----.  .-'),-----. ,--./ ,--,'    ,------.,-.-')   ,----.     
  '  .--./ ( OO'  .-.  '|   \ |  |\ ('-| _.---'|  |OO) '  .-./-')  
  |  |('-. /   |  | |  ||    \|  | )(OO|(_\    |  |  \ |  |_( O- ) 
 /_) |OO  )\_) |  |\|  ||  .     |/ /  |  '--. |  |(_/ |  | .--, \ 
 ||  |`-'|   \ |  | |  ||  |\    |  \_)|  .--',|  |_.'(|  | '. (_/ 
(_'  '--'\    `'  '-'  '|  | \   |    \|  |_)(_|  |    |  '--'  |  
   `-----'      `-----' `--'  `--'     `--'    `--'     `------'   """
matrix_text = r""" _   .-')      ('-.     .-') _   _  .-')           (`-.      
( '.( OO )_   ( OO ).-.(  OO) ) ( \( -O )         ( OO ).    
 ,--.   ,--.) / . --. //     '._ ,------.  ,-.-')(_/.  \_)-. 
 |   `.'   |  | \-.  \ |'--...__)|   /`. ' |  |OO)\  `.'  /  
 |         |.-'-'  |  |'--.  .--'|  /  | | |  |  \ \     /\  
 |  |'.'|  | \| |_.'  |   |  |   |  |_.' | |  |(_/  \   \ |  
 |  |   |  |  |  .-.  |   |  |   |  .  '.',|  |_.' .'    \_) 
 |  |   |  |  |  | |  |   |  |   |  |\  \(_|  |   /  .'.  \  
 `--'   `--'  `--' `--'   `--'   `--' '--' `--'  '--'   '--' """

def display_ascii_art() -> None:
    config_text_lines = config_text.split("\n")
    matrix_text_lines = matrix_text.split("\n")
    for line in config_text_lines:
        print(f"\033[94m{line}\033[0m")
        time.sleep(0.05)
    for line in matrix_text_lines:
        print(f"\033[94m{line}\033[0m")
        time.sleep(0.05)




def validate_int(value_name: str, value_from: int, value_to: int, indentation_lvl: int = 0) -> tuple:
    indent = "\t" * indentation_lvl
    value_name = value_name.lower()
    while True:
        try:
            value = int(input(f"{indent}Enter {value_name} ({value_from}-{value_to}): "))
            if value >= value_from and value <= value_to:
                return value, False
            else:
                print(f"{value_name.capitalize()} must be between: {value_from}-{value_to}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None, True
        except:
            print(f"{indent}Please enter a number with the {value_name}")

def create_time(indentation_lvl: int = 0) -> tuple:
    current_year = datetime.now().year
    
    # Get year first to validate month/day properly
    year, cancelled = validate_int(value_name="year", value_from=current_year, value_to=current_year + 10, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    month, cancelled = validate_int(value_name="month", value_from=1, value_to=12, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
    
    # Determine max days for the given month/year
    if month in [1, 3, 5, 7, 8, 10, 12]:  # 31-day months
        max_days = 31
    elif month in [4, 6, 9, 11]:  # 30-day months
        max_days = 30
    else:  # February
        # Check for leap year
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_days = 29
        else:
            max_days = 28
    
    date, cancelled = validate_int(value_name="date of month", value_from=1, value_to=max_days, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    hour, cancelled = validate_int(value_name="hour", value_from=0, value_to=23, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    minutes, cancelled = validate_int(value_name="minutes", value_from=0, value_to=59, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
    
    formated_time = f"{year}-{month}-{date} {hour}:{minutes}"
    deadline = datetime.strptime(formated_time, "%Y-%m-%d %H:%M")
    return deadline, False


main_help = """
        \033[96m" + "="*60 + "\033[0m
        \033[96m                    PC SETUP MANAGER HELP                   \033[0m
        \033[96m" + "="*60 + "\033[0m
        
        Welcome to the PC Setup Manager CLI! This tool helps you manage 
        computer setups using profiles and setup steps.

        \033[93mMain Commands:\033[0m
          \033[92mprofiles\033[0m   - Manage setup profiles
          \033[92msteps\033[0m      - Manage setup steps
          \033[92mcomputers\033[0m  - Manage computers and track progress
          \033[92mhelp\033[0m       - Show this help menu
          \033[92mexit\033[0m       - Exit the application

        \033[93mWorkflow Overview:\033[0m
          1. Create setup steps (steps → new)
          2. Create profiles and assign steps (profiles → new, profiles → toggle)
          3. Create computers with profiles (computers → new)
          4. Track setup progress (computers → progress, computers → complete)
        
        \033[93mProfile Management (profiles):\033[0m
          • Create profiles to group related setup steps
          • Assign setup steps to profiles
          • View profile contents and manage assignments
        
        \033[93mSetup Steps Management (steps):\033[0m
          • Create individual setup tasks
          • Add instructions or download links
          • View all available steps
        
        \033[93mComputer Management (computers):\033[0m
          • Create computers with assigned profiles
          • Track setup progress with completion status
          • Mark steps as complete/incomplete
          • View remaining tasks and overall progress
        
        \033[93mTips:\033[0m
          • Type 'help' in any submenu for specific commands
          • Use 'exit' to return to previous menu levels
          • Progress is tracked per computer automatically
        
        \033[96m" + "="*60 + "\033[0m
        """

profile_help = """
\033[94mProfile commands:\033[0m
  new    - Create a new profile
  show   - Display all profiles and their assigned steps
  toggle - Add/remove a setup step to/from a profile
  delete - Delete a profile entirely
  exit   - Exit profile management
"""

setup_step_help = """
\033[94mSetup Step commands:\033[0m
  new    - Create a new setup step
  show   - Display all setup steps
  delete - Delete a setup step
  exit   - Exit setup step management
"""

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

main_help = """
\033[94m============================================================\033[0m
\033[94m                    PC SETUP MANAGER HELP                   \033[0m
\033[94m============================================================\033[0m

Welcome to the PC Setup Manager CLI! This tool helps you manage
computer setups using profiles and setup steps.

\033[94mMain Commands:\033[0m
  \033[36mprofiles\033[0m   - Manage setup profiles
  \033[36msteps\033[0m      - Manage setup steps
  \033[36mcomputers\033[0m  - Manage computers and track progress
  \033[36mhelp\033[0m       - Show this help menu
  \033[36mexit\033[0m       - Exit the application

\033[94mWorkflow Overview:\033[0m
  1. Create setup steps (steps → new)
  2. Create profiles and assign steps (profiles → new, profiles → toggle)
  3. Create computers with profiles (computers → new)
  4. Track setup progress (computers → progress, computers → complete)

\033[94mProfile Management (profiles):\033[0m
  • Create profiles to group related setup steps
  • Assign setup steps to profiles
  • View profile contents and manage assignments

\033[94mSetup Steps Management (steps):\033[0m
  • Create individual setup tasks
  • Add instructions or download links
  • View all available steps

\033[94mComputer Management (computers):\033[0m
  • Create computers with assigned profiles
  • Track setup progress with completion status
  • Mark steps as complete/incomplete
  • View remaining tasks and overall progress

\033[94mTips:\033[0m
  • Type 'help' in any submenu for specific commands
  • Use 'exit' to return to previous menu levels
  • Progress is tracked per computer automatically

\033[94m============================================================\033[0m
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



def main() -> None:
    while True:
        try:
            prompt = input("Config Matrix ->")
            prompt = prompt.strip().lower()
        except KeyboardInterrupt:
            print("\n\033[36mShutting down...\033[0m")
            break
        if prompt == "help":
            print(main_help)
        elif prompt == "profiles":
            profile_prompt()
        elif prompt == "steps":
            setup_step_prompt()
        elif prompt == "computers":
            computer_prompt()
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Available options: profiles, steps, computers, help, exit\033[0m")



if __name__ == "__main__":    
    display_ascii_art()
    main()