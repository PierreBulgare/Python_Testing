from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def load_homepage(self):
        self.client.get("/")

    @task(2)
    def show_summary(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task
    def book_page(self):
        self.client.get("/book/Spring Festival/Simply Lift")

    @task
    def points_page(self):
        self.client.get("/points")

    @task
    def logout(self):
        self.client.get("/logout")
