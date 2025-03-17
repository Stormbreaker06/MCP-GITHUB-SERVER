import asyncio
import os
import logging
import sys

# Add current directory to path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_client import GitHubClient
from mcp_server import GitHubMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# Try to import from config file, fall back to environment variables
try:
    from config import GITHUB_API_TOKEN, HOST, PORT
except ImportError:
    logger.info("Config file not found, using environment variables")
    GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
    HOST = os.environ.get("HOST", "localhost")
    PORT = int(os.environ.get("PORT", "8080"))

async def main():
    # Check if API token is set
    if not GITHUB_API_TOKEN:
        logger.error("GitHub API token not found. Please set the GITHUB_API_TOKEN environment variable or update config.py.")
        return
    
    try:
        # Initialize the GitHub client
        logger.info("Initializing GitHub client")
        github_client = GitHubClient(api_token=GITHUB_API_TOKEN)
        
        # Initialize and start the MCP server
        logger.info("Starting GitHub MCP server")
        server = GitHubMCPServer(github_client)
        
        # Handle graceful shutdown
        try:
            await server.start(host=HOST, port=PORT)
            logger.info(f"GitHub MCP server running at http://{HOST}:{PORT}")
            
            # Keep the server running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            await server.stop()
    
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped.")