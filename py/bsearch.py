import argparse
import yaml
import os
import sys
from atproto import Client

# Expected configuration file structure
CONFIG_STRUCTURE = """
Expected config.yaml structure:

credentials:
  handle: your-handle.bsky.social
  app_password: your-app-password
"""


# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Bluesky Search Tool",
        epilog=CONFIG_STRUCTURE,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Path to the configuration YAML file"
    )
    parser.add_argument("search_terms", nargs="+", help="Search terms to query")
    return parser.parse_args()


# Function to load credentials from the YAML configuration file
def load_credentials(config_path):
    if not os.path.isfile(config_path):
        print(f"Error: Configuration file '{config_path}' not found.")
        print(CONFIG_STRUCTURE)
        sys.exit(1)
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            handle = config["credentials"]["handle"]
            app_password = config["credentials"]["app_password"]
            return handle, app_password
    except (yaml.YAMLError, KeyError) as e:
        print(f"Error: Invalid configuration file format.\n{CONFIG_STRUCTURE}")
        sys.exit(1)


# Main function
def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Load credentials from the configuration file
    handle, app_password = load_credentials(args.config)

    # Combine search terms into a single query string
    search_query = " ".join(args.search_terms)

    # Initialize the client
    client = Client()

    # Log in to the Bluesky API
    client.login(handle, app_password)

    # Fetch posts containing the search query
    search_results = client.app.bsky.feed.search_posts({"q": search_query})

    # Display the results
    for post in search_results.posts:
        print(f"User: {post.author.handle}")
        print(f"Post: {post.record.text}")
        print("-" * 40)


if __name__ == "__main__":
    main()
