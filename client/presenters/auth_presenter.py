from services.api_client import ApiClient
from services.auth import AUTH

class AuthPresenter:
    def __init__(self, view):
        self.view = view
        self.api = ApiClient()

    def login(self, email, password):
        try:
            response = self.api.login(email, password)
            AUTH.token = response['accessToken']
            AUTH.user = response['user']
            AUTH.save_auth()
            return True, ""
        except Exception as e:
            AUTH.clear_auth()
            message = str(e)
            if "401" in message:
                return False, "כתובת מייל או סיסמה שגויה"
            return False, message

    def register(self, email, name, password):
        try:
            self.api.register(email, name, password)
            return True, ""
        except Exception as e:
            message = str(e)
            if "422" in message and "already exists" in message:
                return False, "משתמש עם כתובת מייל זו כבר קיים במערכת"
            return False, message
