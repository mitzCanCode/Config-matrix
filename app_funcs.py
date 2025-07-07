from db import session, Apps


def create_app(name: str, download_link: str) -> tuple:
    try:
        new_app = Apps(
            name = name,
            download_link = download_link
        )
        session.add(new_app)
        session.commit()
        return (True, f"{name}({download_link}) app was created", 200)
    
    except Exception as e:
        print(e)
        return (False, f"{name}({download_link}) creation failed", 500)

def retrieve_all_apps() -> tuple:
    try: 
        # Retrieving all apps
        apps = session.query(Apps).all()
        if apps:
            return (True, "Apps retrieved successfully", apps, 200)
        else:
            return (True, "No apps have been created yet", apps, 200)
    except Exception as e:
        return (False, "An error occured while mapping apps", [],500)
        
if __name__ == "__main__":
    status, message, error_code = create_app(name="Apple music", download_link="music.apple.com")
    print(status, message, error_code)
    status, message, error_code = create_app(name="Spotify", download_link="spotify.com")
    print(status, message, error_code)

