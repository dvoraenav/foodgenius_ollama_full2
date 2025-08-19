import json
import os
from pathlib import Path

"""AuthStore: handles saving/loading/clearing user authentication token & info from ~/.foodgenius_auth.json"""


class AuthStore:
    def __init__(self):
        self.token = None
        self.user = None
        self.config_file = Path.home() / ".foodgenius_auth.json"
        self.load_auth()
    
    def save_auth(self):
        """Save authentication data to file"""
        try:
            auth_data = {
                "token": self.token,
                "user": self.user
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(auth_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save auth: {e}")
    
    def load_auth(self):
        """Load authentication data from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                    self.token = auth_data.get("token")
                    self.user = auth_data.get("user")
        except Exception as e:
            print(f"Failed to load auth: {e}")
            # Reset to defaults if loading fails
            self.token = None
            self.user = None
    
    def clear_auth(self):
        """Clear authentication data and remove file"""
        self.token = None
        self.user = None
        try:
            if self.config_file.exists():
                self.config_file.unlink()
        except Exception as e:
            print(f"Failed to clear auth file: {e}")
    
    def is_authenticated(self):
        """Check if user is currently authenticated"""
        return self.token is not None and self.user is not None

AUTH = AuthStore()