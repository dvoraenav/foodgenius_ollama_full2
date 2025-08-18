from services.api_client import ApiClient
from services.auth import AUTH

class AuthPresenter:
    def __init__(self, view):
        self.view = view
        self.api = ApiClient()
    
    def login(self, email, password):
        """Login user and save authentication data"""
        try:
            response = self.api.login(email, password)
            
            # Save to AUTH store
            AUTH.token = response['accessToken']
            AUTH.user = response['user']
            
            # Persist to file
            AUTH.save_auth()
            
            return True
        except Exception as e:
            # Make sure to clear any partial data on error
            AUTH.clear_auth()
            raise e
    
    def register(self, email, name, password):
        """Register new user"""
        try:
            self.api.register(email, name, password)
            return True
        except Exception as e:
            raise e
    
    def logout(self):
        """Logout user and clear all authentication data"""
        AUTH.clear_auth()
        return True