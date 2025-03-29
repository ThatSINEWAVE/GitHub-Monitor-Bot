<div align="center">

# GitHub-Monitor-Bot

A Discord bot that monitors GitHub repositories for star changes and sends notifications to a Discord channel. The bot tracks star additions and removals, provides detailed information about stargazers, and sends personalized thank-you messages.

</div>

## Features

- **Real-time Star Tracking**: Monitors GitHub repositories for star changes at regular intervals
- **Detailed Notifications**: Sends Discord embeds with repository info, stargazer details, and change history
- **Personalized Messages**: Random thank-you messages for new stars and thoughtful responses for removed stars
- **Milestone Celebrations**: Special notifications when repositories reach star milestones (10, 50, 100, etc.)
- **Persistent Data Storage**: Maintains repository data between runs to track changes accurately
- **Error Handling**: Robust logging and error recovery mechanisms

## Planned Features

- **Fork Notifications**: Track when repositories are forked and notify the channel
- **Pull Request Monitoring**: Notify about new PRs, merged PRs, and PR comments
- **Issue Tracking**: Monitor issue creation, updates, and closures
- **Discussion Support**: Track GitHub Discussions activity
- **Profile Follow Tracking**: Monitor user follows and unfollows
- **Customizable Notifications**: Allow users to configure which events they want notifications for
- **Repository Selection**: Choose specific repositories to monitor rather than all public ones

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/GitHub-Monitor-Bot.git
   cd GitHub-Monitor-Bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the `.env.example` template and fill in your credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   GITHUB_TOKEN=your_github_token
   ```

4. Create a `repositories.json` file (can start empty):
   ```json
   {
     "repositories": []
   }
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

The bot can be configured by modifying the `config.py` file or environment variables:

- `CHECK_INTERVAL`: How often to check for star changes (in seconds)
- `DATA_DIR`: Directory to store persistent data
- `REPOSITORIES_FILE`: File to store repository data

## Usage

Once running, the bot will:
1. Connect to your Discord server
2. Start monitoring your GitHub repositories
3. Send notifications to the configured channel for:
   - New stars added
   - Stars removed
   - New repositories created
   - Star milestones reached

<div align="center">

## [Join my Discord server](https://discord.gg/2nHHHBWNDw)

</div>

## Requirements

- Python 3.8+
- discord.py
- aiohttp
- python-dotenv

## Contributing

Contributions are welcome! Please open an issue or pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.