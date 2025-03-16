import httpx
import logging
from typing import Dict, List, Any, Optional

class GitHubClient:
    """
    Client for interacting with the GitHub API.
    """
    
    def __init__(self, api_token: str):
        """
        Initialize the GitHub client with an API token.
        
        Args:
            api_token: GitHub personal access token
        """
        self.api_token = api_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {api_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.logger = logging.getLogger("github_client")
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                            data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the GitHub API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body for POST/PUT requests
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"Making {method} request to {url}")
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, params=params, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=self.headers, params=params, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
    
    async def search_repositories(self, query: str, limit: int = 5, sort: str = "stars", 
                                  order: str = "desc") -> List[Dict]:
        """
        Search for repositories on GitHub.
        
        Args:
            query: Search query
            limit: Maximum number of results
            sort: Sort field (stars, forks, updated)
            order: Sort order (asc, desc)
            
        Returns:
            List of repository data
        """
        params = {"q": query, "per_page": limit, "sort": sort, "order": order}
        response = await self._make_request("GET", "/search/repositories", params=params)
        return response.get("items", [])
    
    async def get_repository(self, owner: str, repo: str) -> Dict:
        """
        Get information about a specific repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository data
        """
        return await self._make_request("GET", f"/repos/{owner}/{repo}")
    
    async def get_issues(self, owner: str, repo: str, state: str = "open", 
                         limit: int = 10) -> List[Dict]:
        """
        Get issues for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            limit: Maximum number of results
            
        Returns:
            List of issue data
        """
        params = {"state": state, "per_page": limit}
        return await self._make_request("GET", f"/repos/{owner}/{repo}/issues", params=params)
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                           labels: List[str] = None) -> Dict:
        """
        Create a new issue in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body/description
            labels: List of labels to apply
            
        Returns:
            Created issue data
        """
        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
            
        return await self._make_request("POST", f"/repos/{owner}/{repo}/issues", data=data)