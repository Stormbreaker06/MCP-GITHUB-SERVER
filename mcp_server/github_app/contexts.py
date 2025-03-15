import requests

class GitHubContext:
    BASE_URL = "https://api.github.com"

    @staticmethod
    def get_repository(owner, repo_name):
        url = f"{GitHubContext.BASE_URL}/repos/{owner}/{repo_name}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Returns a dict with repository data
        return None
