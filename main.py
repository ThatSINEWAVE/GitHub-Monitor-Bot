import asyncio
import os
from services.github_api import GitHubAPI
from services.discord_bot import DiscordBot
from config.config import Config
from utils.logger import setup_logger

# Set up logger
logger = setup_logger("main")


class GitHubStarMonitor:
    def __init__(self):
        self.github_api = GitHubAPI()
        self.discord_bot = DiscordBot(self.github_api)
        self.running = False

    async def start(self):
        """Start the monitor."""
        self.running = True
        logger.info("Starting GitHub Star Monitor")

        # Start Discord bot in a separate task
        discord_task = asyncio.create_task(self.run_discord_bot())

        # Start GitHub monitoring in a separate task
        monitor_task = asyncio.create_task(self.monitor_github_stars())

        try:
            # Wait for both tasks to complete
            await asyncio.gather(discord_task, monitor_task)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
        except Exception as e:
            logger.error(f"Error in main process: {e}")
        finally:
            self.running = False
            await self.github_api.close_session()
            logger.info("Monitor stopped.")

    async def run_discord_bot(self):
        """Run the Discord bot."""
        try:
            await self.discord_bot.start()
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
            self.running = False

    async def monitor_github_stars(self):
        """Monitor GitHub repositories for star changes."""
        logger.info("Starting GitHub star monitoring with 5-minute intervals")

        # Initial load of repository data
        old_repos = self.github_api.load_repositories_data()

        # If this is the first run or data is empty, fetch fresh data
        if not old_repos:
            logger.info("No existing repository data found. Fetching initial data...")
            raw_repos = await self.github_api.get_all_public_repositories()
            old_repos = self.github_api.parse_repository_data(raw_repos)
            old_repos = await self.github_api.update_stargazers_for_repos(old_repos)
            await self.github_api.save_repositories_data(old_repos)
            logger.info(f"Initialized data for {len(old_repos)} repositories")

        while self.running:
            try:
                logger.info("Checking for star changes...")

                # Fetch the latest repository data
                raw_repos = await self.github_api.get_all_public_repositories()
                new_repos = self.github_api.parse_repository_data(raw_repos)

                # Update stargazers for each repository
                new_repos = await self.github_api.update_stargazers_for_repos(new_repos)

                # Compare star counts
                changes = self.github_api.compare_stars(old_repos, new_repos)

                # Process changes
                if changes:
                    logger.info(f"Found {len(changes)} changes to process")
                    for change in changes:
                        repo_name = change["repo"]["full_name"]
                        if change["type"] == "added":
                            logger.info(
                                f"Detected {change['difference']} new star(s) for {repo_name}"
                            )
                            await self.discord_bot.send_star_update(change)
                        elif change["type"] == "removed":
                            logger.info(
                                f"Detected {change['difference']} removed star(s) for {repo_name}"
                            )
                            await self.discord_bot.send_star_update(change)
                        elif change["type"] == "new":
                            logger.info(f"Detected new repository: {repo_name}")

                    # Save the updated repository data
                    await self.github_api.save_repositories_data(new_repos)
                    old_repos = new_repos
                else:
                    logger.info("No star changes detected")

                # Wait before checking again
                logger.info(
                    f"Waiting {Config.CHECK_INTERVAL} seconds before next check..."
                )
                await asyncio.sleep(Config.CHECK_INTERVAL)

            except asyncio.CancelledError:
                logger.info("Monitor task cancelled")
                break
            except Exception as e:
                logger.error(f"Error while monitoring GitHub stars: {e}")
                await asyncio.sleep(Config.CHECK_INTERVAL)


if __name__ == "__main__":
    # Ensure all required directories exist
    Config.ensure_directories()

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    monitor = GitHubStarMonitor()

    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
