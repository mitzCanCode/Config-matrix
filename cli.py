from config_mtrx_module.profiles import profile_prompt
from config_mtrx_module.steps import setup_step_prompt
from config_mtrx_module.computers import computer_prompt
from config_mtrx_module.technicians import sign_in_sign_up_cli
import time


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

main_help = f"""
\033[96m" + {"="*60} + "\033[0m
\033[96m                    PC SETUP MANAGER HELP                   \033[0m
\033[96m" + {"="*60} + "\033[0m

Welcome to the PC Setup Manager CLI! This tool helps you manage 
computer setups using profiles and setup steps.

\033[93mMain Commands:\033[0m
\t\033[92mprofiles\033[0m   - Manage setup profiles
\t\033[92msteps\033[0m      - Manage setup steps
\t\033[92mcomputers\033[0m  - Manage computers and track progress
\t\033[92mhelp\033[0m       - Show this help menu
\t\033[92mexit\033[0m       - Exit the application

\033[93mWorkflow Overview:\033[0m
\t1. Create setup steps (steps → new)
\t2. Create profiles and assign steps (profiles → new, profiles → toggle)
\t3. Create computers with profiles (computers → new)
\t4. Track setup progress (computers → progress, computers → complete)

\033[93mProfile Management (profiles):\033[0m
\t• Create profiles to group related setup steps
\t• Assign setup steps to profiles
\t• View profile contents and manage assignments

\033[93mSetup Steps Management (steps):\033[0m
\t• Create individual setup tasks
\t• Add instructions or download links
\t• View all available steps

\033[93mComputer Management (computers):\033[0m
\t• Create computers with assigned profiles
\t• Track setup progress with completion status
\t• Mark steps as complete/incomplete
\t• View remaining tasks and overall progress

\033[93mTips:\033[0m
\t• Type 'help' in any submenu for specific commands
\t• Use 'exit' to return to previous menu levels
\t• Progress is tracked per computer automatically

\033[96m" + {"="*60} + "\033[0m
"""


def main() -> None:
    _, _, username, password, _ = sign_in_sign_up_cli()
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
            computer_prompt(username)
        elif prompt == "exit":
            break
        else:
            print("\033[94mUnknown command. Available options: profiles, steps, computers, help, exit\033[0m")


if __name__ == "__main__":    
    display_ascii_art()
    main()