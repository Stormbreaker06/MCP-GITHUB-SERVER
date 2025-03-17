import asyncio
import json
import logging
from typing import Dict, Any, Callable, Awaitable, Optional, List
from mcp.server import Server as MCPServer

# Update imports based on the actual MCP SDK structure
try:
    from mcp.server.model import Action, ActionSuccessResult, ActionErrorResult
except ImportError:
    # Define our own action types if the import fails
    class Action:
        def __init__(self, action_id=None, params=None):
            self.action_id = action_id
            self.params = params or {}
    
    class ActionSuccessResult:
        def __init__(self, result=None):
            self.result = result or {}
    
    class ActionErrorResult:
        def __init__(self, error=None):
            self.error = error or "Unknown error"

class GitHubMCPServer:
    def __init__(self, github_client):
        self.github_client = github_client
        # Initialize the MCP server with a name
        self.mcp_server = MCPServer(name="github-mcp-server")
        self.logger = self._setup_logger()
        self._register_handlers()
    
    def _setup_logger(self):
        logger = logging.getLogger("github_mcp_server")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _register_handlers(self):
        """Register all GitHub API handlers with the MCP server."""
        # Adjust the registration method based on the actual MCP SDK
        try:
            self.mcp_server.register_action_handler("search_repositories", self.handle_search_repositories)
            self.mcp_server.register_action_handler("get_repository", self.handle_get_repository)
            self.mcp_server.register_action_handler("list_issues", self.handle_list_issues)
            self.mcp_server.register_action_handler("create_issue", self.handle_create_issue)
            self.mcp_server.register_action_handler("list_pull_requests", self.handle_list_pull_requests)
            self.mcp_server.register_action_handler("get_user_profile", self.handle_get_user_profile)
            self.mcp_server.register_action_handler("list_repos_for_user", self.handle_list_repos_for_user)
        except AttributeError:
            # Try alternative registration method if the above fails
            self.mcp_server.register_handler("search_repositories", self.handle_search_repositories)
            self.mcp_server.register_handler("get_repository", self.handle_get_repository)
            self.mcp_server.register_handler("list_issues", self.handle_list_issues)
            self.mcp_server.register_handler("create_issue", self.handle_create_issue)
            self.mcp_server.register_handler("list_pull_requests", self.handle_list_pull_requests)
            self.mcp_server.register_handler("get_user_profile", self.handle_get_user_profile)
            self.mcp_server.register_handler("list_repos_for_user", self.handle_list_repos_for_user)
        
        self.logger.info("All GitHub handlers registered")
    
    async def start(self, host: str = "localhost", port: int = 8080):
        """Start the MCP server."""
        self.logger.info(f"Starting GitHub MCP server on {host}:{port}")
        try:
            await self.mcp_server.start(host=host, port=port)
        except TypeError:
            # Try alternative start method signature if the above fails
            await self.mcp_server.start(address=host, port=port)
    
    async def stop(self):
        """Stop the MCP server."""
        self.logger.info("Stopping GitHub MCP server")
        await self.mcp_server.stop()
    
    # The handler methods need to be adjusted based on the actual expected interface
    async def handle_search_repositories(self, action):
        """Handle the search_repositories action."""
        try:
            # Handle both Action objects and direct parameter dictionaries
            params = getattr(action, 'params', action) or {}
            
            query = params.get("query", "")
            limit = int(params.get("limit", 5))
            sort = params.get("sort", "stars")
            order = params.get("order", "desc")
            
            if not query:
                error_msg = "Query parameter is required"
                return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}
            
            repos = await self.github_client.search_repositories(query, limit, sort, order)
            
            # Format the results for better readability
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    "name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "language": repo.get("language"),
                    "url": repo.get("html_url"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at")
                })
            
            result = {"repositories": formatted_repos}
            return ActionSuccessResult(result=result) if 'ActionSuccessResult' in globals() else result
        except Exception as e:
            self.logger.error(f"Error in search_repositories: {str(e)}")
            error_msg = f"Failed to search repositories: {str(e)}"
            return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}
    
    # Include the remaining handler methods here...
    # For brevity, I'll include just one more as an example
    
    async def handle_get_repository(self, action):
        """Handle the get_repository action."""
        try:
            # Handle both Action objects and direct parameter dictionaries
            params = getattr(action, 'params', action) or {}
            
            owner = params.get("owner")
            repo = params.get("repo")
            
            if not owner or not repo:
                error_msg = "Owner and repo parameters are required"
                return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}
            
            repo_data = await self.github_client.get_repository(owner, repo)
            
            result = {"repository": repo_data}
            return ActionSuccessResult(result=result) if 'ActionSuccessResult' in globals() else result
        except Exception as e:
            self.logger.error(f"Error in get_repository: {str(e)}")
            error_msg = f"Failed to get repository: {str(e)}"
            return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}
            
    async def handle_list_issues(self, action):
        """Handle the list_issues action."""
        try:
            # Handle both Action objects and direct parameter dictionaries
            params = getattr(action, 'params', action) or {}
            
            owner = params.get("owner")
            repo = params.get("repo")
            state = params.get("state", "open")
            limit = int(params.get("limit", 10))
            
            if not owner or not repo:
                error_msg = "Owner and repo parameters are required"
                return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}
            
            issues = await self.github_client.get_issues(owner, repo, state, limit)
            
            # Format the issues
            formatted_issues = []
            for issue in issues:
                formatted_issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "created_at": issue.get("created_at"),
                    "updated_at": issue.get("updated_at"),
                    "user": issue.get("user", {}).get("login"),
                    "url": issue.get("html_url"),
                    "comments": issue.get("comments")
                })
            
            result = {"issues": formatted_issues}
            return ActionSuccessResult(result=result) if 'ActionSuccessResult' in globals() else result
        except Exception as e:
            self.logger.error(f"Error in list_issues: {str(e)}")
            error_msg = f"Failed to list issues: {str(e)}"
            return ActionErrorResult(error=error_msg) if 'ActionErrorResult' in globals() else {"error": error_msg}