import asyncio
import json
import logging
from typing import Dict, Any, Callable, Awaitable, Optional, List
from mcp.server import Server as MCPServer
from mcp.server.model import Action, ActionSuccessResult, ActionErrorResult

class GitHubMCPServer:
    def __init__(self, github_client):
        self.github_client = github_client
        self.mcp_server = MCPServer()
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
        self.mcp_server.register_action_handler("search_repositories", self.handle_search_repositories)
        self.mcp_server.register_action_handler("get_repository", self.handle_get_repository)
        self.mcp_server.register_action_handler("list_issues", self.handle_list_issues)
        self.mcp_server.register_action_handler("create_issue", self.handle_create_issue)
        self.mcp_server.register_action_handler("list_pull_requests", self.handle_list_pull_requests)
        self.mcp_server.register_action_handler("get_user_profile", self.handle_get_user_profile)
        self.mcp_server.register_action_handler("list_repos_for_user", self.handle_list_repos_for_user)
        self.logger.info("All GitHub handlers registered")
    
    async def start(self, host: str = "localhost", port: int = 8080):
        """Start the MCP server."""
        self.logger.info(f"Starting GitHub MCP server on {host}:{port}")
        await self.mcp_server.start(host=host, port=port)
    
    async def stop(self):
        """Stop the MCP server."""
        self.logger.info("Stopping GitHub MCP server")
        await self.mcp_server.stop()
    
    async def handle_search_repositories(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the search_repositories action."""
        try:
            query = action.params.get("query", "")
            limit = int(action.params.get("limit", 5))
            sort = action.params.get("sort", "stars")
            order = action.params.get("order", "desc")
            
            if not query:
                return ActionErrorResult(error="Query parameter is required")
            
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
            
            return ActionSuccessResult(result={"repositories": formatted_repos})
        except Exception as e:
            self.logger.error(f"Error in search_repositories: {str(e)}")
            return ActionErrorResult(error=f"Failed to search repositories: {str(e)}")
    
    async def handle_get_repository(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the get_repository action."""
        try:
            owner = action.params.get("owner")
            repo = action.params.get("repo")
            
            if not owner or not repo:
                return ActionErrorResult(error="Owner and repo parameters are required")
            
            repo_data = await self.github_client.get_repository(owner, repo)
            
            return ActionSuccessResult(result={"repository": repo_data})
        except Exception as e:
            self.logger.error(f"Error in get_repository: {str(e)}")
            return ActionErrorResult(error=f"Failed to get repository: {str(e)}")
    
    async def handle_list_issues(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the list_issues action."""
        try:
            owner = action.params.get("owner")
            repo = action.params.get("repo")
            state = action.params.get("state", "open")
            limit = int(action.params.get("limit", 10))
            
            if not owner or not repo:
                return ActionErrorResult(error="Owner and repo parameters are required")
            
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
            
            return ActionSuccessResult(result={"issues": formatted_issues})
        except Exception as e:
            self.logger.error(f"Error in list_issues: {str(e)}")
            return ActionErrorResult(error=f"Failed to list issues: {str(e)}")
    
    async def handle_create_issue(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the create_issue action."""
        try:
            owner = action.params.get("owner")
            repo = action.params.get("repo")
            title = action.params.get("title")
            body = action.params.get("body", "")
            labels = action.params.get("labels", [])
            
            if not owner or not repo or not title:
                return ActionErrorResult(error="Owner, repo, and title parameters are required")
            
            issue = await self.github_client.create_issue(owner, repo, title, body, labels)
            
            return ActionSuccessResult(result={"issue": {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "url": issue.get("html_url")
            }})
        except Exception as e:
            self.logger.error(f"Error in create_issue: {str(e)}")
            return ActionErrorResult(error=f"Failed to create issue: {str(e)}")
    
    async def handle_list_pull_requests(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the list_pull_requests action."""
        try:
            owner = action.params.get("owner")
            repo = action.params.get("repo")
            state = action.params.get("state", "open")
            limit = int(action.params.get("limit", 10))
            
            if not owner or not repo:
                return ActionErrorResult(error="Owner and repo parameters are required")
            
            pull_requests = await self.github_client.get_pull_requests(owner, repo, state, limit)
            
            # Format the pull requests
            formatted_prs = []
            for pr in pull_requests:
                formatted_prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                    "user": pr.get("user", {}).get("login"),
                    "url": pr.get("html_url")
                })
            
            return ActionSuccessResult(result={"pull_requests": formatted_prs})
        except Exception as e:
            self.logger.error(f"Error in list_pull_requests: {str(e)}")
            return ActionErrorResult(error=f"Failed to list pull requests: {str(e)}")
    
    async def handle_get_user_profile(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the get_user_profile action."""
        try:
            username = action.params.get("username")
            
            if not username:
                return ActionErrorResult(error="Username parameter is required")
            
            user_data = await self.github_client.get_user(username)
            
            # Format the user data
            user_profile = {
                "login": user_data.get("login"),
                "name": user_data.get("name"),
                "bio": user_data.get("bio"),
                "company": user_data.get("company"),
                "location": user_data.get("location"),
                "public_repos": user_data.get("public_repos"),
                "followers": user_data.get("followers"),
                "following": user_data.get("following"),
                "created_at": user_data.get("created_at"),
                "url": user_data.get("html_url")
            }
            
            return ActionSuccessResult(result={"user": user_profile})
        except Exception as e:
            self.logger.error(f"Error in get_user_profile: {str(e)}")
            return ActionErrorResult(error=f"Failed to get user profile: {str(e)}")
    
    async def handle_list_repos_for_user(self, action: Action) -> ActionSuccessResult | ActionErrorResult:
        """Handle the list_repos_for_user action."""
        try:
            username = action.params.get("username")
            limit = int(action.params.get("limit", 10))
            sort = action.params.get("sort", "updated")
            
            if not username:
                return ActionErrorResult(error="Username parameter is required")
            
            repos = await self.github_client.get_user_repos(username, limit, sort)
            
            # Format the repositories
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "url": repo.get("html_url"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at")
                })
            
            return ActionSuccessResult(result={"repositories": formatted_repos})
        except Exception as e:
            self.logger.error(f"Error in list_repos_for_user: {str(e)}")
            return ActionErrorResult(error=f"Failed to list repositories for user: {str(e)}")