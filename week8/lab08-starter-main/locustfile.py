import random
from locust import HttpUser, task, between, events

class BooksUser(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 3)
    
    def on_start(self):
        self.created_book_ids = []

    @task(3)
    def browse_books(self):
        self.client.get("/books", name="GET /books")

    @task(2)
    def read_book_detail(self):
        book_id = random.randint(1, 100)
        self.client.get(f"/books/{book_id}", name="GET /books/{id}")

    @task(1)
    def create_and_delete_book(self):
        payload = {
            "title": f"Test Book {random.randint(1000, 9999)}",
            "author": "Automated Tester",
            "year": 2024
        }
        response = self.client.post("/books", json=payload, name="POST /books")
        
        if response.status_code == 201:
            data = response.json()
            if data and "id" in data:
                created_id = data["id"]
                self.client.delete(f"/books/{created_id}", name="DELETE /books/{id}")

    @task(1)
    def search_by_year(self):
        if random.random() < 0.01:
            with self.client.get("/books?year=invalid_err", name="GET /books?year=search", catch_response=True) as resp:
                resp.failure("Giả lập lỗi Server 500 ngẫu nhiên (1% probability)")
        else:
            self.client.get("/books?year=2024", name="GET /books?year=search")