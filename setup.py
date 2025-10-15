#!/usr/bin/env python3
"""
Setup script for Reddit scraper
"""

import os
import sys
import subprocess
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return
    
    # Create .env file
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your Reddit API credentials")


def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def main():
    """Main setup function"""
    print("Setting up Reddit scraper...")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    install_dependencies()
    
    print("\n" + "=" * 40)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your Reddit API credentials")
    print("2. Get Reddit API credentials from: https://www.reddit.com/prefs/apps")
    print("3. Run: python main.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()

