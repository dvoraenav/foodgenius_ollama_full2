from services.api_client import ApiClient

class SearchPresenter:
    def __init__(self, view):
        self.view = view
        self.api = ApiClient()

    def search(self, query):
        """
        מבצע חיפוש מתכונים לפי מחרוזת חיפוש
        :param query: מחרוזת חיפוש (למשל "cake")
        :return: רשימת מתכונים
        """
        recipes = self.api.get_external_recipes(query or '')
        return recipes
