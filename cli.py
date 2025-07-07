from profile_funcs import create_profile
from app_funcs import create_app, retrieve_all_apps
config_text = """
                             .-') _                                
                            ( OO ) )                               
   .-----.  .-'),-----. ,--./ ,--,'    ,------.,-.-')   ,----.     
  '  .--./ ( OO'  .-.  '|   \ |  |\ ('-| _.---'|  |OO) '  .-./-')  
  |  |('-. /   |  | |  ||    \|  | )(OO|(_\    |  |  \ |  |_( O- ) 
 /_) |OO  )\_) |  |\|  ||  .     |/ /  |  '--. |  |(_/ |  | .--, \ 
 ||  |`-'|   \ |  | |  ||  |\    |  \_)|  .--',|  |_.'(|  | '. (_/ 
(_'  '--'\    `'  '-'  '|  | \   |    \|  |_)(_|  |    |  '--'  |  
   `-----'      `-----' `--'  `--'     `--'    `--'     `------'   
""" 
matrix_text = """
 _   .-')      ('-.     .-') _   _  .-')         ) (`-.      
( '.( OO )_   ( OO ).-.(  OO) ) ( \( -O )         ( OO ).    
 ,--.   ,--.) / . --. //     '._ ,------.  ,-.-')(_/.  \_)-. 
 |   `.'   |  | \-.  \ |'--...__)|   /`. ' |  |OO)\  `.'  /  
 |         |.-'-'  |  |'--.  .--'|  /  | | |  |  \ \     /\  
 |  |'.'|  | \| |_.'  |   |  |   |  |_.' | |  |(_/  \   \ |  
 |  |   |  |  |  .-.  |   |  |   |  .  '.',|  |_.' .'    \_) 
 |  |   |  |  |  | |  |   |  |   |  |\  \(_|  |   /  .'.  \  
 `--'   `--'  `--' `--'   `--'   `--' '--' `--'  '--'   '--' 
"""



def profile_prompt():
    while True:
        prompt  = input("Profiles ->")
        prompt = prompt.lower()
        if prompt == "help":
            print("No help menu for profiles yet")
        elif prompt == "new":
            profile_name = input("\tProfile name:")
            status, message, _ = create_profile(name=profile_name)
            if status:
                print(f"\t\033[92m{message}\033[0m")
            else:
                print(f"\t\033[91m{message}\033[0m")
        elif prompt == "show":
            
        elif prompt == "exit":
            break
        else:
            print("Unknown command run 'help' for instructions on the profiles module")




def app_prompt():
    while True:
        prompt  = input("Apps ->")
        prompt = prompt.lower()
        if prompt == "help":
            print("No help menu for apps yet")
        elif prompt == "new":
            app_name = input("\tApp name:")
            download_link = input("\tDownload link:")
            status, message, _ = create_app(name=app_name, download_link=download_link)
            if status:
                print(f"\t\033[92m{message}\033[0m")
            else:
                print(f"\t\033[91m{message}\033[0m")
        elif prompt == "show":
            status, message, apps, _ = retrieve_all_apps()
            if not status:
                print(message) 
                continue
            if not apps:
                print(message)
            else:
                for app in apps:
                    print(f"\t{app.name}({app.download_link})")
        elif prompt == "exit":
            break
        else:
            print("Unknown command run 'help' for instructions on the apps module")
print(config_text)
print(matrix_text)

while True:
    prompt = input("Config matrix ->")
    prompt = prompt.lower()
    if prompt == "h":
        print("No help menu main yet")
    elif prompt == "p":
        profile_prompt()