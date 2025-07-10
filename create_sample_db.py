from config_mtrx_module.db import session, Technicians, Computers, Profiles, SetupSteps
from datetime import datetime, timedelta
import bcrypt

def hash_password(password):
    """Hash a password using bcrypt"""
    bytes_pass = password.encode()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(bytes_pass, salt)
    return hashed_password.decode()

def clear_database():
    """Clear all existing data from the database"""
    session.query(Computers).delete()
    session.query(Profiles).delete()
    session.query(SetupSteps).delete()
    session.query(Technicians).delete()
    session.commit()
    print("Database cleared.")

def create_technicians():
    """Create sample technicians with proper security"""
    # Using more realistic names and secure passwords
    technician_data = [
        {"name": "Alice Johnson", "email": "alice.johnson@company.com", "password": "SecurePass2024!"},
        {"name": "Robert Chen", "email": "robert.chen@company.com", "password": "TechSupport#789"},
        {"name": "Maria Rodriguez", "email": "maria.rodriguez@company.com", "password": "ITAdmin$456"},
        {"name": "James Wilson", "email": "james.wilson@company.com", "password": "ConfigMaster@123"},
        {"name": "Sarah Kim", "email": "sarah.kim@company.com", "password": "SystemSetup321"},
        {"name": "user", "email": "user@domain.com", "password": "Password123@"},
    ]

    technicians = []
    for tech_data in technician_data:
        # Hash the password before storing
        hashed_password = hash_password(tech_data["password"])
        technician = Technicians(name=tech_data["name"], password=hashed_password)
        technicians.append(technician)
    
    session.add_all(technicians)
    session.commit()
    print(f"Created {len(technicians)} technicians with secure passwords.")
    print("Note: In production, use a proper authentication system like OAuth or LDAP.")

def create_setup_steps():
    """Create comprehensive setup steps with proper download links"""
    steps = [
        # System Setup
        SetupSteps(name="Install macOS Sonoma", download_link="https://apps.apple.com/us/app/macos-sonoma/id6450717509"),
        SetupSteps(name="Configure System Preferences", download_link="https://support.apple.com/guide/mac-help/change-system-preferences-mh15217/mac"),
        SetupSteps(name="Enable FileVault Encryption", download_link="https://support.apple.com/en-us/HT204837"),
        SetupSteps(name="Configure Network Settings", download_link="https://support.apple.com/guide/mac-help/set-up-a-wifi-network-connection-mchlp2650/mac"),
        SetupSteps(name="Install System Updates", download_link="https://support.apple.com/en-us/HT201541"),
        
        # Security
        SetupSteps(name="Configure Firewall", download_link="https://support.apple.com/guide/mac-help/block-connections-to-your-mac-with-a-firewall-mh34041/mac"),
        SetupSteps(name="Install Malware Protection", download_link="https://www.malwarebytes.com/mac"),
        SetupSteps(name="Configure SSH Keys", download_link="https://docs.github.com/en/authentication/connecting-to-github-with-ssh"),
        
        # Development Tools
        SetupSteps(name="Install Xcode Command Line Tools", download_link="https://developer.apple.com/xcode/resources/"),
        SetupSteps(name="Install Visual Studio Code", download_link="https://code.visualstudio.com/download"),
        SetupSteps(name="Install Git", download_link="https://git-scm.com/download/mac"),
        SetupSteps(name="Install Docker Desktop", download_link="https://www.docker.com/products/docker-desktop/"),
        SetupSteps(name="Install Node.js", download_link="https://nodejs.org/en/download/"),
        SetupSteps(name="Install Python 3", download_link="https://www.python.org/downloads/macos/"),
        SetupSteps(name="Install Homebrew", download_link="https://brew.sh/"),
        
        # Productivity Software
        SetupSteps(name="Install Google Chrome", download_link="https://www.google.com/chrome/"),
        SetupSteps(name="Install Mozilla Firefox", download_link="https://www.mozilla.org/en-US/firefox/new/"),
        SetupSteps(name="Install Microsoft Office 365", download_link="https://www.office.com/"),
        SetupSteps(name="Install Slack", download_link="https://slack.com/downloads/mac"),
        SetupSteps(name="Install Zoom", download_link="https://zoom.us/download"),
        SetupSteps(name="Install 1Password", download_link="https://1password.com/downloads/mac/"),
        
        # Creative Tools
        SetupSteps(name="Install Adobe Creative Cloud", download_link="https://creativecloud.adobe.com/apps/download/creative-cloud"),
        SetupSteps(name="Install Photoshop", download_link="https://www.adobe.com/products/photoshop.html"),
        SetupSteps(name="Install Illustrator", download_link="https://www.adobe.com/products/illustrator.html"),
        SetupSteps(name="Install Final Cut Pro", download_link="https://www.apple.com/final-cut-pro/"),
        SetupSteps(name="Install Logic Pro", download_link="https://www.apple.com/logic-pro/"),
        
        # Specialized Tools
        SetupSteps(name="Install Figma", download_link="https://www.figma.com/downloads/"),
        SetupSteps(name="Install Postman", download_link="https://www.postman.com/downloads/"),
        SetupSteps(name="Install TablePlus", download_link="https://tableplus.com/"),
        SetupSteps(name="Install VPN Client", download_link="https://support.apple.com/guide/mac-help/set-up-a-vpn-connection-on-mac-mchlp2963/mac"),
        
        # Configuration Tasks
        SetupSteps(name="Configure Time Machine Backup", download_link="https://support.apple.com/en-us/HT201250"),
        SetupSteps(name="Setup iCloud Integration", download_link="https://support.apple.com/en-us/HT204025"),
        SetupSteps(name="Configure Email Accounts", download_link="https://support.apple.com/guide/mail/add-email-accounts-mail11374/mac"),
        SetupSteps(name="Install Printer Drivers", download_link="https://support.apple.com/guide/mac-help/add-a-printer-on-mac-mh14004/mac"),
        SetupSteps(name="Configure Active Directory", download_link="https://support.apple.com/guide/directory-utility/welcome/mac")
    ]
    
    session.add_all(steps)
    session.commit()
    print(f"Created {len(steps)} setup steps.")

def create_profiles():
    """Create comprehensive profiles with realistic step assignments"""
    # Get all steps for assignment
    all_steps = session.query(SetupSteps).all()
    
    # Full Stack Developer profile
    dev_profile = Profiles(name="Full Stack Developer")
    dev_steps = [
        "Install macOS Sonoma",
        "Configure System Preferences",
        "Enable FileVault Encryption",
        "Configure Network Settings",
        "Install System Updates",
        "Configure Firewall",
        "Install Xcode Command Line Tools",
        "Install Visual Studio Code",
        "Install Git",
        "Install Docker Desktop",
        "Install Node.js",
        "Install Python 3",
        "Install Homebrew",
        "Configure SSH Keys",
        "Install Google Chrome",
        "Install Mozilla Firefox",
        "Install Slack",
        "Install Zoom",
        "Install 1Password",
        "Install Postman",
        "Install TablePlus",
        "Configure Time Machine Backup",
        "Setup iCloud Integration"
    ]
    dev_profile.setup_steps_to_follow = [step for step in all_steps if step.name in dev_steps]
    
    # Creative Professional profile
    creative_profile = Profiles(name="Creative Professional")
    creative_steps = [
        "Install macOS Sonoma",
        "Configure System Preferences",
        "Enable FileVault Encryption",
        "Configure Network Settings",
        "Install System Updates",
        "Configure Firewall",
        "Install Google Chrome",
        "Install Adobe Creative Cloud",
        "Install Photoshop",
        "Install Illustrator",
        "Install Final Cut Pro",
        "Install Logic Pro",
        "Install Figma",
        "Install Slack",
        "Install Zoom",
        "Install 1Password",
        "Configure Time Machine Backup",
        "Setup iCloud Integration",
        "Configure Email Accounts",
        "Install Printer Drivers"
    ]
    creative_profile.setup_steps_to_follow = [step for step in all_steps if step.name in creative_steps]
    
    # Business Professional profile
    business_profile = Profiles(name="Business Professional")
    business_steps = [
        "Install macOS Sonoma",
        "Configure System Preferences",
        "Enable FileVault Encryption",
        "Configure Network Settings",
        "Install System Updates",
        "Configure Firewall",
        "Install Malware Protection",
        "Install Google Chrome",
        "Install Microsoft Office 365",
        "Install Slack",
        "Install Zoom",
        "Install 1Password",
        "Install VPN Client",
        "Configure Time Machine Backup",
        "Setup iCloud Integration",
        "Configure Email Accounts",
        "Install Printer Drivers",
        "Configure Active Directory"
    ]
    business_profile.setup_steps_to_follow = [step for step in all_steps if step.name in business_steps]
    
    # Basic User profile
    basic_profile = Profiles(name="Basic User")
    basic_steps = [
        "Install macOS Sonoma",
        "Configure System Preferences",
        "Enable FileVault Encryption",
        "Configure Network Settings",
        "Install System Updates",
        "Configure Firewall",
        "Install Malware Protection",
        "Install Google Chrome",
        "Install Slack",
        "Install Zoom",
        "Configure Time Machine Backup",
        "Setup iCloud Integration",
        "Configure Email Accounts"
    ]
    basic_profile.setup_steps_to_follow = [step for step in all_steps if step.name in basic_steps]
    
    # System Administrator profile
    admin_profile = Profiles(name="System Administrator")
    admin_steps = [
        "Install macOS Sonoma",
        "Configure System Preferences",
        "Enable FileVault Encryption",
        "Configure Network Settings",
        "Install System Updates",
        "Configure Firewall",
        "Install Malware Protection",
        "Install Xcode Command Line Tools",
        "Install Git",
        "Install Docker Desktop",
        "Install Python 3",
        "Install Homebrew",
        "Configure SSH Keys",
        "Install Google Chrome",
        "Install Mozilla Firefox",
        "Install Slack",
        "Install Zoom",
        "Install 1Password",
        "Install Postman",
        "Install TablePlus",
        "Install VPN Client",
        "Configure Time Machine Backup",
        "Setup iCloud Integration",
        "Configure Email Accounts",
        "Install Printer Drivers",
        "Configure Active Directory"
    ]
    admin_profile.setup_steps_to_follow = [step for step in all_steps if step.name in admin_steps]
    
    profiles = [dev_profile, creative_profile, business_profile, basic_profile, admin_profile]
    session.add_all(profiles)
    session.commit()
    print(f"Created {len(profiles)} profiles with realistic configurations.")

def create_computers():
    """Create sample computers with realistic models and assignments"""
    # Get technicians and profiles
    technicians = session.query(Technicians).all()
    profiles = session.query(Profiles).all()
    
    # Create computers with varied deadlines and realistic naming
    today = datetime.now()
    computers = []
    
    for i in range(50):
        computer = Computers(
            name=f"Computer {i + 1}",
            deadline=today + timedelta(days=(i % 10 + 1)),
            technician=technicians[i % len(technicians)],
            profile=profiles[i % len(profiles)]
        )
        computers.append(computer)
    
    session.add_all(computers)
    session.commit()
    print(f"Created {len(computers)} computers with realistic models and assignments.")

def mark_some_steps_complete():
    """Mark some steps as complete for realistic progress simulation"""
    computers = session.query(Computers).all()
    
    # Simulate different progress levels for all 50 computers
    import random
    
    for i, computer in enumerate(computers):
        if computer.profile and computer.profile.setup_steps_to_follow:
            total_steps = len(computer.profile.setup_steps_to_follow)
            # Random progress between 0% and 90%
            progress_percentage = random.uniform(0, 0.9)
            steps_to_complete_count = int(total_steps * progress_percentage)
            
            if steps_to_complete_count > 0:
                steps_to_complete = computer.profile.setup_steps_to_follow[:steps_to_complete_count]
                computer.setup_steps.extend(steps_to_complete)
                print(f"  - {computer.name}: {steps_to_complete_count}/{total_steps} steps completed ({progress_percentage*100:.1f}%)")
    
    session.commit()
    print("\nMarked various steps as complete to simulate realistic progress for all computers.")

def print_database_summary():
    """Print a comprehensive summary of the created database"""
    print("\n" + "="*80)
    print("                        DATABASE SUMMARY")
    print("="*80)
    
    # Technicians
    technicians = session.query(Technicians).all()
    print(f"\n📋 TECHNICIANS ({len(technicians)}):")
    for i, tech in enumerate(technicians, 1):
        print(f"  {i}. {tech.name} (Password: Securely Hashed)")
    
    # Setup Steps
    steps = session.query(SetupSteps).all()
    print(f"\n⚙️  SETUP STEPS ({len(steps)}):")
    categories = {"System Setup": [], "Security": [], "Development Tools": [], 
                  "Productivity Software": [], "Creative Tools": [], "Specialized Tools": [], 
                  "Configuration Tasks": []}
    
    for step in steps:
        if any(word in step.name.lower() for word in ["install macos", "configure system", "install system"]):
            categories["System Setup"].append(step.name)
        elif any(word in step.name.lower() for word in ["firewall", "malware", "ssh", "filevault"]):
            categories["Security"].append(step.name)
        elif any(word in step.name.lower() for word in ["xcode", "git", "docker", "node", "python", "homebrew"]):
            categories["Development Tools"].append(step.name)
        elif any(word in step.name.lower() for word in ["chrome", "firefox", "office", "slack", "zoom", "1password"]):
            categories["Productivity Software"].append(step.name)
        elif any(word in step.name.lower() for word in ["adobe", "photoshop", "illustrator", "final cut", "logic"]):
            categories["Creative Tools"].append(step.name)
        elif any(word in step.name.lower() for word in ["figma", "postman", "tableplus", "vpn"]):
            categories["Specialized Tools"].append(step.name)
        else:
            categories["Configuration Tasks"].append(step.name)
    
    for category, steps_list in categories.items():
        if steps_list:
            print(f"    {category}: {len(steps_list)} steps")
    
    # Profiles
    profiles = session.query(Profiles).all()
    print(f"\n👥 PROFILES ({len(profiles)}):")
    for i, profile in enumerate(profiles, 1):
        print(f"  {i}. {profile.name} ({len(profile.setup_steps_to_follow)} steps configured)")
    
    # Computers
    computers = session.query(Computers).all()
    print(f"\n💻 COMPUTERS ({len(computers)}):")
    for i, computer in enumerate(computers, 1):
        tech_name = computer.technician.name if computer.technician else "Unassigned"
        profile_name = computer.profile.name if computer.profile else "No Profile"
        completed_steps = len(computer.setup_steps)
        total_steps = len(computer.profile.setup_steps_to_follow) if computer.profile else 0
        progress = f"{completed_steps}/{total_steps}" if total_steps > 0 else "0/0"
        progress_percent = f"({completed_steps/total_steps*100:.1f}%)" if total_steps > 0 else "(0%)"
        deadline_str = computer.deadline.strftime("%Y-%m-%d") if computer.deadline else "No deadline"
        print(f"  {i}. {computer.name}")
        print(f"     └── Technician: {tech_name} | Profile: {profile_name}")
        print(f"     └── Progress: {progress} {progress_percent} | Deadline: {deadline_str}")
    
    print("\n" + "="*80)
    print("🔒 SECURITY NOTE: All passwords are properly hashed with salt")
    print("📝 RECOMMENDATION: Use OAuth/LDAP authentication in production")
    print("="*80)

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

