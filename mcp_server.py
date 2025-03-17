import asyncio
import json
import logging
import sys
from typing import Dict, Any, Callable, Awaitable, Optional, List
from mcp.server import Server as MCPServer

# Define our own action types
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
        # Check which handler methods actually exist in this class
        existing_handlers = {}
        
        potential_handlers = {
            "search_repositories": "handle_search_repositories",
            "get_repository": "handle_get_repository",
            "list_issues": "handle_list_issues",
            "create_issue": "handle_create_issue",
            "list_pull_requests": "handle_list_pull_requests",
            "get_user_profile": "handle_get_user_profile",
            "list_repos_for_user": "handle_list_repos_for_user"
        }
        
        # Only include handlers that actually exist in this class
        for action_name, method_name in potential_handlers.items():
            if hasattr(self, method_name):
                existing_handlers[action_name] = getattr(self, method_name)
                self.logger.info(f"Found handler method: {method_name}")
            else:
                self.logger.warning(f"Handler method not found: {method_name}")
        
        # Check if request_handlers exists and is a dictionary
        if hasattr(self.mcp_server, 'request_handlers') and isinstance(self.mcp_server.request_handlers, dict):
            self.logger.info("Using request_handlers dictionary for registration")
            
            # Add our existing handlers to the request_handlers dictionary
            for action_name, handler_func in existing_handlers.items():
                self.mcp_server.request_handlers[action_name] = handler_func
                self.logger.info(f"Registered handler for {action_name}")
                
            self.logger.info(f"Registered {len(existing_handlers)} GitHub handlers")
        else:
            # If we don't find request_handlers, look for other handler registration mechanisms
            for attr_name in dir(self.mcp_server):
                attr = getattr(self.mcp_server, attr_name)
                # Check if this is a method that might be used for registration
                if callable(attr) and ('register' in attr_name.lower() or 'add' in attr_name.lower() or 'handle' in attr_name.lower()):
                    self.logger.info(f"Found potential registration method: {attr_name}")
            
            self.logger.error("Could not find appropriate handler registration mechanism")
            raise RuntimeError("Cannot find a way to register handlers with this MCPServer implementation")
    
    async def start(self, host: str = "localhost", port: int = 8080):
        """Start the MCP server."""
        self.logger.info(f"Starting GitHub MCP server on {host}:{port}")
        
        # Set up standard input and output streams for the server
        read_stream = asyncio.StreamReader()
        write_stream = asyncio.StreamWriter(sys.stdout.buffer, None)
        
        # Create initialization options
        initialization_options = self.mcp_server.create_initialization_options()
        
        self.logger.info("Running MCP server with standard I/O streams")
        try:
            # Run the server with the required arguments
            await self.mcp_server.run(read_stream, write_stream, initialization_options)
        except Exception as e:
            self.logger.error(f"Error running server: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the MCP server."""
        self.logger.info("Stopping GitHub MCP server")
        # There's no clear stop method based on the dir output,
        # but if there was one, we'd call it here
    
    # Define only the handler method that we know exists
    async def handle_search_repositories(self, action):
        """Handle the search_repositories action."""
        try:
            # Handle both Action objects and direct parameter dictionaries
            params = getattr(action, 'params', action) if action else {}
            if isinstance(params, dict) is False:
                params = {}
            
            query = params.get("query", "")
            limit = int(params.get("limit", 5))
            sort = params.get("sort", "stars")
            order = params.get("order", "desc")
            
            if not query:
                error_msg = "Query parameter is required"
                return ActionErrorResult(error=error_msg)
            
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
            return ActionSuccessResult(result=result)
        except Exception as e:
            self.logger.error(f"Error in search_repositories: {str(e)}")
            error_msg = f"Failed to search repositories: {str(e)}"
            return ActionErrorResult(error=error_msg)