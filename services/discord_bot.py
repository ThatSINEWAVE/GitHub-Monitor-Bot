import discord
import datetime
import random
import asyncio
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger("discord_bot")


class DiscordBot:
    def __init__(self, github_api):
        self.client = discord.Client(intents=discord.Intents.default())
        self.channel = None
        self.github_api = github_api

        # Thank you messages for new stars
        self.thank_you_messages = [
            "Thank you so much for the star! Your support means a lot! ✨",
            "Woohoo! Thanks for starring our repository! You're awesome! 🌟",
            "A new star has brightened our day! Thank you for your support! 🙏",
            "Thanks for the star! We appreciate your interest in our project! 💫",
            "Every star fuels our motivation! Thank you for your support! 🚀",
            "Your star makes a difference! Thank you for supporting our work! 💯",
            "Thanks for the star! We're thrilled you found our project interesting! 🎉",
        ]

        # Messages for when stars are removed
        self.star_removed_messages = [
            "We're sad to see you go! Thanks for your support while it lasted. 💔",
            "A star has fallen, but we appreciate the time you spent with us! 🌠",
            "We'll miss your star! Hope to win you back in the future! 👋",
            "Your star will be missed. We'll keep working to improve! 🔄",
            "Sorry to see you unstar. We'd love to know how we can improve! 📝",
            "Every star matters to us. We'll miss yours! 💫",
            "Thanks for the time you supported us with your star! 🙏",
        ]

    async def start(self):
        """Start the Discord bot."""

        @self.client.event
        async def on_ready():
            logger.info(f"Logged in as {self.client.user.name} ({self.client.user.id})")
            self.channel = self.client.get_channel(Config.DISCORD_CHANNEL_ID)
            if not self.channel:
                logger.error(
                    f"Could not find channel with ID {Config.DISCORD_CHANNEL_ID}"
                )
            else:
                logger.info(f"Connected to channel: {self.channel.name}")

        await self.client.start(Config.DISCORD_TOKEN)

    async def send_star_update(self, change):
        """Send a formatted embed message about star changes."""
        if not self.channel:
            logger.error("Discord channel not found, can't send message")
            return

        # Only proceed if there are actual star changes (added or removed)
        if change["type"] not in ["added", "removed"]:
            return

        repo = change["repo"]
        logger.info(
            f"Preparing to send {change['type']} star notification for {repo['full_name']}"
        )

        embed = discord.Embed(
            title=f"Star Update for {repo['name']}",
            url=repo["url"],
            color=self.get_embed_color(change["type"]),
            timestamp=datetime.datetime.utcnow(),
        )

        # Set the repository thumbnail
        embed.set_thumbnail(url=f"https://github.com/fluidicon.png")

        # Add repository information
        embed.add_field(
            name="Repository",
            value=f"[{repo['full_name']}]({repo['url']})",
            inline=False,
        )

        if change["type"] == "added":
            # Get recent stargazers
            star_count_diff = change.get("difference", 1)
            users = change.get("users", [])

            if star_count_diff == 1 and users:
                latest_stargazer = users[0]
                embed.description = f"🌟 **New Star Added by [{latest_stargazer['username']}]({latest_stargazer['profile']})**"
                embed.set_author(
                    name=latest_stargazer["username"],
                    url=latest_stargazer["profile"],
                    icon_url=latest_stargazer["avatar"],
                )

                # Add a random thank-you message
                thank_msg = random.choice(self.thank_you_messages)
                embed.add_field(name="Message", value=thank_msg, inline=False)
                logger.info(
                    f"Sending new star notification from {latest_stargazer['username']}"
                )
            elif star_count_diff == 1:
                # Fallback if no user information is available
                embed.description = f"🌟 **New Star Added!**"
                # Add a random thank-you message even without knowing who starred
                thank_msg = random.choice(self.thank_you_messages)
                embed.add_field(name="Message", value=thank_msg, inline=False)
                logger.info("Sending new star notification (unknown user)")
            else:
                # Multiple stars added
                embed.description = f"🌟 **{star_count_diff} New Stars Added!**"
                logger.info(f"Sending notification for {star_count_diff} new stars")

                # List users who starred if available
                if users:
                    users_list = "\n".join(
                        [
                            f"• [{user['username']}]({user['profile']})"
                            for user in users[: min(star_count_diff, len(users))]
                        ]
                    )
                    embed.add_field(
                        name="New Stargazers", value=users_list, inline=False
                    )

                embed.add_field(
                    name="Message",
                    value="Thank you all for your amazing support! Each star motivates us to keep improving! 🙏✨",
                    inline=False,
                )

            embed.add_field(
                name="Stars",
                value=f"⭐ {change['old_stars']} → **{change['new_stars']}**",
                inline=True,
            )

        elif change["type"] == "removed":
            star_count_diff = change.get("difference", 1)
            users = change.get("users", [])

            if star_count_diff == 1 and users:
                removed_user = users[0]
                embed.description = f"💔 **Star Removed by [{removed_user['username']}]({removed_user['profile']})**"
                embed.set_author(
                    name=removed_user["username"],
                    url=removed_user["profile"],
                    icon_url=removed_user["avatar"],
                )

                # Add a random message for removed star
                removed_msg = random.choice(self.star_removed_messages)
                embed.add_field(name="Message", value=removed_msg, inline=False)
                logger.info(
                    f"Sending removed star notification for {removed_user['username']}"
                )
            elif star_count_diff == 1:
                # Fallback if no user information is available
                embed.description = f"💔 **Star Removed**"
                # Add a random message for removed star
                removed_msg = random.choice(self.star_removed_messages)
                embed.add_field(name="Message", value=removed_msg, inline=False)
                logger.info("Sending removed star notification (unknown user)")
            else:
                # Multiple stars removed
                embed.description = f"💔 **{star_count_diff} Stars Removed**"
                logger.info(f"Sending notification for {star_count_diff} removed stars")

                # List users who removed stars if available
                if users:
                    users_list = "\n".join(
                        [
                            f"• [{user['username']}]({user['profile']})"
                            for user in users[: min(star_count_diff, len(users))]
                        ]
                    )
                    embed.add_field(
                        name="Users Who Removed Stars", value=users_list, inline=False
                    )

                embed.add_field(
                    name="Message",
                    value="We're sorry to see some stars go. We're continuously working to improve our project and hope to earn your support again! 🙏",
                    inline=False,
                )

            embed.add_field(
                name="Stars",
                value=f"⭐ {change['old_stars']} → **{change['new_stars']}**",
                inline=True,
            )

        # Add additional repository details
        if repo.get("description"):
            embed.add_field(
                name="Description", value=repo["description"][:1024], inline=False
            )

        if repo.get("language"):
            embed.add_field(name="Language", value=repo["language"], inline=True)

        embed.add_field(name="Forks", value=str(repo["forks"]), inline=True)

        # Add milestone messages for certain star counts
        if change["type"] == "added":
            current_stars = change["new_stars"]
            if current_stars in [10, 50, 100, 500, 1000, 5000, 10000]:
                embed.add_field(
                    name="🏆 Milestone Reached!",
                    value=f"Congratulations! The repository has reached **{current_stars} stars**! Thank you to everyone who has supported this project!",
                    inline=False,
                )
                logger.info(
                    f"Milestone reached: {current_stars} stars for {repo['full_name']}"
                )

        # Add footer with timestamp info
        embed.set_footer(
            text=f"Created: {self.format_date(repo['created_at'])} | Last updated: {self.format_date(repo['updated_at'])}"
        )

        try:
            await self.channel.send(embed=embed)
            logger.info(
                f"Successfully sent star update notification for {repo['name']}"
            )
        except Exception as e:
            logger.error(f"Failed to send star update: {e}")

    def get_embed_color(self, change_type):
        """Get the appropriate color for the embed based on the change type."""
        if change_type == "added":
            return discord.Color.green()
        elif change_type == "removed":
            return discord.Color.red()
        else:  # new
            return discord.Color.blue()

    def format_date(self, date_string):
        """Format the date from GitHub API format to a more readable format."""
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
            return date.strftime("%b %d, %Y")
        except:
            return date_string
