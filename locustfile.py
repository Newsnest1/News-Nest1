from locust import HttpUser, task, between

class NewsNestUser(HttpUser):
    """
    Simulates a user browsing the News-Nest API.
    """
    # Wait time between tasks for each user, in seconds
    wait_time = between(1, 5)

    @task
    def get_main_feed(self):
        """
        Task to simulate a user fetching the main feed.
        This will hit the endpoint that returns all articles, grouped by category.
        """
        self.client.get("/v1/feed")

    @task(3)
    def get_categorized_feed(self):
        """
        Task to simulate a user fetching a specific category feed.
        This is weighted to be called 3x more often than the main feed.
        """
        # A list of categories to choose from for the test
        categories = ["Technology", "Sports", "Business", "Politics", "Weather"]
        import random
        category = random.choice(categories)
        self.client.get(f"/v1/feed?category={category}", name="/v1/feed?category=[category]") 