from services.api_client import ApiClient
from services.auth import AUTH
class AuthPresenter:
    def __init__(self, v): self.v,self.api=v,ApiClient()
    def login(self,e,p): d=self.api.login(e,p); AUTH.token=d['accessToken']; AUTH.user=d['user']; return True
    def register(self,e,n,p): self.api.register(e,n,p); return True
