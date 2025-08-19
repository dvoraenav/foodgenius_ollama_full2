from services.api_client import ApiClient

class RecipePresenter:
    def __init__(self, view):
        self.view = view
        self.api = ApiClient()

    def load(self, recipe_id):
        """טוען מתכון לפי מזהה"""
        return self.api.recipe(recipe_id)

    def chat(self, recipe_id, question):
        """שולח שאלה על המתכון ל־AI"""
        return self.api.chat(question, recipe_id)
