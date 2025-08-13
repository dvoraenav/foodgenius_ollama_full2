from services.api_client import ApiClient
class RecipePresenter:
    def __init__(self,v): self.v,self.api=v,ApiClient()
    def load(self,r): return self.api.recipe(r)
    def veganize(self,r): return self.api.transform({'recipe_id':r,'goal':'veganize'})
    def scale(self,r,f,t): return self.api.transform({'recipe_id':r,'goal':'scale','servings_from':f,'servings_to':t})
    def veganize_llm(self,r): return self.api.transform_llm_vegan(r)
    def chat(self,r,q): return self.api.chat(q,r)
