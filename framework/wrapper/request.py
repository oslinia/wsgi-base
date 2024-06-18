from ..service import HttpRequest


class Request(HttpRequest):
    def env(self, name: str):
        return self.http.environ.get(name)

    def query(self, name: str):
        return self.http.call.query.get(name)

    def cookie(self, name: str):
        return self.http.call.cookie.get(name)

    def form(self, name: str):
        return self.http.call.form.data.get(name)

    def upload(self, name: str):
        return self.http.call.form.upload.get(name)
