import json
import aiohttp
import os
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger("github_api")


class GitHubAPI:
    def __init__(self):
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Star-Monitor-Bot",
        }
        self.session = None

        # Ensure data directory exists
        Config.ensure_directories()

    async def start_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_all_public_repositories(self):
        """Fetch all public repositories, handling pagination."""
        await self.start_session()

        repositories = []
        page = 1
        per_page = 100

        while True:
            params = {
                "per_page": per_page,
                "page": page,
                "visibility": "public",
                "sort": "updated",
            }

            try:
                async with self.session.get(
                    Config.GITHUB_API_URL, headers=self.headers, params=params
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error fetching repositories: {response.status} - {await response.text()}"
                        )
                        break

                    repos_page = await response.json()
                    if not repos_page:
                        break

                    # Filter to only public repos
                    public_repos = [
                        repo for repo in repos_page if not repo.get("private", False)
                    ]
                    repositories.extend(public_repos)

                    # Check if we need to paginate more
                    if len(repos_page) < per_page:
                        break

                    page += 1
            except Exception as e:
                logger.error(f"Exception while fetching repositories: {e}")
                break

        return repositories

    async def get_all_stargazers(self, repo_full_name):
        """Get all users who starred the repository."""
        await self.start_session()

        stargazers = []
        page = 1
        per_page = 100

        while True:
            try:
                url = f"https://api.github.com/repos/{repo_full_name}/stargazers"
                params = {"per_page": per_page, "page": page}

                async with self.session.get(
                    url, headers=self.headers, params=params
                ) as response:
                    if response.status == 200:
                        stargazers_data = await response.json()
                        if not stargazers_data:
                            break

                        page_stargazers = [
                            {
                                "username": user["login"],
                                "profile": user["html_url"],
                                "avatar": user["avatar_url"],
                            }
                            for user in stargazers_data
                        ]
                        stargazers.extend(page_stargazers)

                        # Check if we need to paginate more
                        if len(stargazers_data) < per_page:
                            break

                        page += 1
                    else:
                        logger.error(
                            f"Error fetching stargazers: {response.status} - {await response.text()}"
                        )
                        break
            except Exception as e:
                logger.error(f"Exception while fetching stargazers: {e}")
                break

        return stargazers

    async def get_recent_stargazers(self, repo_full_name, count=5):
        """Get the most recent users who starred the repository."""
        await self.start_session()

        stargazers = []
        try:
            url = f"https://api.github.com/repos/{repo_full_name}/stargazers"
            params = {"per_page": count}

            async with self.session.get(
                url, headers=self.headers, params=params
            ) as response:
                if response.status == 200:
                    stargazers_data = await response.json()
                    stargazers = [
                        {
                            "username": user["login"],
                            "profile": user["html_url"],
                            "avatar": user["avatar_url"],
                        }
                        for user in stargazers_data
                    ]
                else:
                    logger.error(
                        f"Error fetching stargazers: {response.status} - {await response.text()}"
                    )
        except Exception as e:
            logger.error(f"Exception while fetching stargazers: {e}")

        return stargazers

    def parse_repository_data(self, repositories):
        """Extract relevant information from repositories."""
        parsed_data = []

        for repo in repositories:
            parsed_data.append(
                {
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "url": repo["html_url"],
                    "description": repo.get("description", ""),
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo.get("language"),
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "stargazers": [],  # Initialize empty stargazers list
                }
            )

        return parsed_data

    async def update_stargazers_for_repos(self, repositories):
        """Update the stargazers list for each repository."""
        for repo in repositories:
            stargazers = await self.get_all_stargazers(repo["full_name"])
            repo["stargazers"] = stargazers
            logger.info(
                f"Updated stargazers for {repo['full_name']}: {len(stargazers)} users"
            )

        return repositories

    async def save_repositories_data(self, repositories):
        """Save repositories data to JSON file."""
        try:
            with open(Config.REPOSITORIES_FILE, "w") as file:
                json.dump({"repositories": repositories}, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save repositories data: {e}")
            return False

    def load_repositories_data(self):
        """Load repositories data from JSON file."""
        try:
            with open(Config.REPOSITORIES_FILE, "r") as file:
                data = json.load(file)
                return data.get("repositories", [])
        except FileNotFoundError:
            logger.info(
                f"No existing repositories file found at {Config.REPOSITORIES_FILE}. Creating a new one."
            )
            return []
        except Exception as e:
            logger.error(f"Failed to load repositories data: {e}")
            return []

    def compare_stars(self, old_repos, new_repos):
        """Compare star counts between old and new repository data."""
        changes = []

        # Create a lookup dictionary for fast access
        old_repos_dict = {repo["id"]: repo for repo in old_repos}

        for new_repo in new_repos:
            repo_id = new_repo["id"]

            if repo_id in old_repos_dict:
                old_repo = old_repos_dict[repo_id]
                old_stars = old_repo["stars"]
                new_stars = new_repo["stars"]

                # Get stargazers from old repository data
                old_stargazers = old_repo.get("stargazers", [])
                new_stargazers = new_repo.get("stargazers", [])

                # Create username sets for easier comparison
                old_usernames = {user["username"] for user in old_stargazers}
                new_usernames = {user["username"] for user in new_stargazers}

                if new_stars > old_stars:
                    # Find users who added stars
                    added_users = new_usernames - old_usernames
                    added_stargazers = [
                        user
                        for user in new_stargazers
                        if user["username"] in added_users
                    ]

                    changes.append(
                        {
                            "type": "added",
                            "repo": new_repo,
                            "old_stars": old_stars,
                            "new_stars": new_stars,
                            "difference": new_stars - old_stars,
                            "users": added_stargazers,
                        }
                    )
                elif new_stars < old_stars:
                    # Find users who removed stars
                    removed_users = old_usernames - new_usernames
                    removed_stargazers = [
                        user
                        for user in old_stargazers
                        if user["username"] in removed_users
                    ]

                    changes.append(
                        {
                            "type": "removed",
                            "repo": new_repo,
                            "old_stars": old_stars,
                            "new_stars": new_stars,
                            "difference": old_stars - new_stars,
                            "users": removed_stargazers,
                        }
                    )
            else:
                # New repository
                changes.append(
                    {"type": "new", "repo": new_repo, "stars": new_repo["stars"]}
                )

        return changes
