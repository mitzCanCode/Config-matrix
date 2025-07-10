from config_mtrx_module.db import session, Technicians, Computers, Profiles, SetupSteps
from datetime import datetime, timedelta

def clear_database():
    """Clear all existing data from the database"""
    session.query(Computers).delete()
    session.query(Profiles).delete()
    session.query(SetupSteps).delete()
    session.query(Technicians).delete()
    session.commit()
    print("Database cleared.")

def create_technicians():
    """Create sample technicians"""
    technicians = [
        Technicians(name="Alice Johnson", password="alice123"),
        Technicians(name="Bob Smith", password="bob123"),
        Technicians(name="Charlie Davis", password="charlie123"),
        Technicians(name="Diana Wilson", password="diana123")
    ]
    
    session.add_all(technicians)
    session.commit()
    print(f"Created {len(technicians)} technicians.")

def create_setup_steps():
    """Create sample setup steps"""
    steps = [
        SetupSteps(name="Install Operating System", download_link="https://support.apple.com/en-us/HT201372"),
        SetupSteps(name="Configure System Preferences", download_link="System Preferences > General"),
        SetupSteps(name="Install Visual Studio Code", download_link="https://code.visualstudio.com/download"),
        SetupSteps(name="Install Git", download_link="https://git-scm.com/download/mac"),
        SetupSteps(name="Install Docker", download_link="https://www.docker.com/products/docker-desktop"),
        SetupSteps(name="Configure SSH Keys", download_link="https://docs.github.com/en/authentication/connecting-to-github-with-ssh"),
        SetupSteps(name="Install Chrome Browser", download_link="https://www.google.com/chrome/"),
        SetupSteps(name="Install Slack", download_link="https://slack.com/downloads/mac"),
        SetupSteps(name="Install Photoshop", download_link="https://www.adobe.com/products/photoshop.html"),
        SetupSteps(name="Install Final Cut Pro", download_link="https://www.apple.com/final-cut-pro/"),
        SetupSteps(name="Configure Network Settings", download_link="System Preferences > Network"),
        SetupSteps(name="Install Antivirus Software", download_link="https://www.malwarebytes.com/mac")
    ]
    
    session.add_all(steps)
    session.commit()
    print(f"Created {len(steps)} setup steps.")

def create_profiles():
    """Create sample profiles with assigned steps"""
    # Get all steps for assignment
    all_steps = session.query(SetupSteps).all()
    
    # Developer profile
    dev_profile = Profiles(name="Developer")
    dev_steps = [
        "Install Operating System",
        "Configure System Preferences", 
        "Install Visual Studio Code",
        "Install Git",
        "Install Docker",
        "Configure SSH Keys",
        "Install Chrome Browser",
        "Install Slack",
        "Configure Network Settings"
    ]
    dev_profile.setup_steps_to_follow = [step for step in all_steps if step.name in dev_steps]
    
    # Producer profile
    producer_profile = Profiles(name="Producer")
    producer_steps = [
        "Install Operating System",
        "Configure System Preferences",
        "Install Chrome Browser",
        "Install Slack",
        "Install Photoshop",
        "Install Final Cut Pro",
        "Configure Network Settings"
    ]
    producer_profile.setup_steps_to_follow = [step for step in all_steps if step.name in producer_steps]
    
    # Basic office profile
    office_profile = Profiles(name="Office Worker")
    office_steps = [
        "Install Operating System",
        "Configure System Preferences",
        "Install Chrome Browser",
        "Install Slack",
        "Configure Network Settings",
        "Install Antivirus Software"
    ]
    office_profile.setup_steps_to_follow = [step for step in all_steps if step.name in office_steps]
    
    profiles = [dev_profile, producer_profile, office_profile]
    session.add_all(profiles)
    session.commit()
    print(f"Created {len(profiles)} profiles.")

def create_computers():
    """Create sample computers with different technicians and profiles"""
    # Get technicians and profiles
    technicians = session.query(Technicians).all()
    profiles = session.query(Profiles).all()
    
    # Create computers with varied deadlines
    today = datetime.now()
    computers = [
        Computers(
            name="MacBook Pro 001",
            deadline=today + timedelta(days=3),
            technician=technicians[0],  # Alice
            profile=profiles[0]  # Developer
        ),
        Computers(
            name="iMac Studio 001",
            deadline=today + timedelta(days=7),
            technician=technicians[1],  # Bob
            profile=profiles[1]  # Producer
        ),
        Computers(
            name="MacBook Air 001",
            deadline=today + timedelta(days=5),
            technician=technicians[2],  # Charlie
            profile=profiles[2]  # Office Worker
        ),
        Computers(
            name="Mac Mini 001",
            deadline=today + timedelta(days=10),
            technician=technicians[0],  # Alice
            profile=profiles[0]  # Developer
        ),
        Computers(
            name="MacBook Pro 002",
            deadline=today + timedelta(days=2),
            technician=technicians[3],  # Diana
            profile=profiles[1]  # Producer
        )
    ]
    
    session.add_all(computers)
    session.commit()
    print(f"Created {len(computers)} computers.")

def mark_some_steps_complete():
    """Mark some steps as complete for demonstration"""
    computers = session.query(Computers).all()
    
    # Mark first few steps complete for the first computer
    if computers:
        first_computer = computers[0]
        if first_computer.profile and first_computer.profile.setup_steps_to_follow:
            # Mark first 2 steps as complete
            steps_to_complete = first_computer.profile.setup_steps_to_follow[:2]
            first_computer.setup_steps.extend(steps_to_complete)
            
        # Mark some steps complete for second computer
        if len(computers) > 1:
            second_computer = computers[1]
            if second_computer.profile and second_computer.profile.setup_steps_to_follow:
                # Mark first 3 steps as complete
                steps_to_complete = second_computer.profile.setup_steps_to_follow[:3]
                second_computer.setup_steps.extend(steps_to_complete)
    
    session.commit()
    print("Marked some steps as complete for demonstration.")

def print_database_summary():
    """Print a summary of the created database"""
    print("\n=== Database Summary ===")
    
    # Technicians
    technicians = session.query(Technicians).all()
    print(f"\nTechnicians ({len(technicians)}):")
    for tech in technicians:
        print(f"  - {tech.name}")
    
    # Setup Steps
    steps = session.query(SetupSteps).all()
    print(f"\nSetup Steps ({len(steps)}):")
    for step in steps:
        print(f"  - {step.name}")
    
    # Profiles
    profiles = session.query(Profiles).all()
    print(f"\nProfiles ({len(profiles)}):")
    for profile in profiles:
        print(f"  - {profile.name} ({len(profile.setup_steps_to_follow)} steps)")
    
    # Computers
    computers = session.query(Computers).all()
    print(f"\nComputers ({len(computers)}):")
    for computer in computers:
        tech_name = computer.technician.name if computer.technician else "Unassigned"
        profile_name = computer.profile.name if computer.profile else "No Profile"
        completed_steps = len(computer.setup_steps)
        total_steps = len(computer.profile.setup_steps_to_follow) if computer.profile else 0
        print(f"  - {computer.name} | {tech_name} | {profile_name} | {completed_steps}/{total_steps} steps")

if __name__ == "__main__":
    print("Creating sample database...")
    
    # Clear existing data
    clear_database()
    
    # Create sample data
    create_technicians()
    create_setup_steps()
    create_profiles()
    create_computers()
    mark_some_steps_complete()
    
    print("\nSample database created successfully!")
    print_database_summary()

