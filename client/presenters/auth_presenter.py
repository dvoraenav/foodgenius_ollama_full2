from services.api_client import ApiClient
from services.auth import AUTH

class AuthPresenter:
    """
    AuthPresenter הוא מתווך (Presenter) בין ה-View לבין שירותי ה-API עבור פעולות Authentication.
    תפקידו:
        - לקבל קלט מהמשתמש (ממשק המשתמש / View)
        - לבצע קריאה ל-API (מודל)
        - לעדכן את ה-AUTH ולשלוח תוצאות חזרה ל-View
    """

    def __init__(self, view):
        """
        אתחול ה-AuthPresenter.

        :param view: האובייקט שמייצג את ממשק המשתמש (View)
        """
        self.view = view
        self.api = ApiClient()

    def login(self, email, password):
        """
        מבצע כניסה למערכת עם כתובת מייל וסיסמה.

        :param email: כתובת המייל של המשתמש
        :param password: סיסמת המשתמש
        :return: tuple[bool, str] - True אם ההתחברות הצליחה, יחד עם הודעה ריקה. אחרת False והודעת שגיאה.
        """
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
        """
        מבצע הרשמה למערכת עם כתובת מייל, שם וסיסמה.

        :param email: כתובת המייל של המשתמש
        :param name: שם המשתמש
        :param password: סיסמה
        :return: tuple[bool, str] - True אם ההרשמה הצליחה, יחד עם הודעה ריקה. אחרת False והודעת שגיאה.
        """
        try:
            self.api.register(email, name, password)
            return True, ""
        except Exception as e:
            message = str(e)
            if ("422" in message or "400" in message) and ("already exists" in message or "already registered" in message):
                return False, "משתמש עם כתובת מייל זו כבר קיים במערכת"
            return False, message
