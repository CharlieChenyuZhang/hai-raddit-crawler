#!/usr/bin/env python3
"""
Script to help set up Reddit API credentials
"""

import os

def create_env_file():
    """Create .env file with Reddit API credentials"""
    
    print("=" * 60)
    print("REDDIT API CREDENTIALS SETUP")
    print("=" * 60)
    print()
    print("To fix the 401 errors, you need to set up Reddit API credentials.")
    print("Follow these steps:")
    print()
    print("1. Go to https://www.reddit.com/prefs/apps")
    print("2. Click 'Create App' or 'Create Another App'")
    print("3. Fill in the form:")
    print("   - Name: hai-reddit-crawler (or any name you prefer)")
    print("   - App type: Select 'script'")
    print("   - Description: Reddit data scraper for research")
    print("   - About URL: Leave blank")
    print("   - Redirect URI: http://localhost:8080")
    print("4. Click 'Create app'")
    print("5. Note down the Client ID and Client Secret")
    print()
    
    # Get credentials from user
    client_id = input("Enter your Reddit Client ID: ").strip()
    client_secret = input("Enter your Reddit Client Secret: ").strip()
    user_agent = input("Enter User Agent (or press Enter for default): ").strip()
    
    if not user_agent:
        user_agent = "hai-reddit-crawler/1.0"
    
    # Create .env file content
    env_content = f"""# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID={client_id}
REDDIT_CLIENT_SECRET={client_secret}
REDDIT_USER_AGENT={user_agent}

# Optional: Reddit username and password for authenticated requests
# Leave these blank for read-only access
REDDIT_USERNAME=
REDDIT_PASSWORD=
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print()
        print("✅ .env file created successfully!")
        print("You can now run the scraper with: python main.py")
        print()
        print("Note: The scraper will work in read-only mode without username/password.")
        print("If you want to access private subreddits or have higher rate limits,")
        print("you can add your Reddit username and password to the .env file.")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print()
        print("Please create the .env file manually with the following content:")
        print("-" * 40)
        print(env_content)
        print("-" * 40)

if __name__ == "__main__":
    create_env_file()
