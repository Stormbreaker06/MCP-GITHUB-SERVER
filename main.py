import asyncio
import json
import os
from mcp.server import Server
from github_client import GitHubClient


from config import GITHUB_API_TOKEN
github_client = GitHubClient(api_token=GITHUB_API_TOKEN)
# Initialize GitHub client with your API token
github_client = GitHubClient(api_token=os.environ.get("GITHUB_API_TOKEN"))

# Set up MCP server handlers
async def handle_search_repos(params):
    query = params.get("query", "")
    limit = int(params.get("limit", 5))
    results = await github_client.search_repositories(query, limit)
    return {"repositories": results}

async def handle_view_issues(params):
    owner = params.get("owner")
    repo = params.get("repo")
    state = params.get("state", "open")
    issues = await github_client.get_issues(owner, repo, state)
    return {"issues": issues}

# Main entry point
async def main():
    # Create MCP server
    server = Server()
    
    # Register handlers
    server.register_handler("search_repositories", handle_search_repos)
    server.register_handler("view_issues", handle_view_issues)
    
    # Start the server
    print("Starting MCP GitHub server...")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())