from services.api_client import ApiClient
class SearchPresenter:
    def __init__(self,v): self.v,self.api=v,ApiClient()
    def search(self,t): return self.api.search(t or '')
