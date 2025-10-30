# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

SaveRestrictedContentBot (TG-Content-Bot-Pro) is a Telegram bot for cloning messages from both public and private channels. It uses a hybrid architecture with Telethon for bot operations and Pyrogram for userbot operations to access restricted content. The bot includes traffic monitoring, batch downloading, and MongoDB-based session management.

## Commands

### Running the Bot

```bash
# Using Docker (recommended)
cd TG-Content-Bot-Pro
docker-compose up -d
docker-compose logs -f

# Manual deployment
cd TG-Content-Bot-Pro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m main

# Using start script
cd TG-Content-Bot-Pro
./start.sh
```

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug logging
LOG_LEVEL=DEBUG python3 -m main

# Run tests (if available)
# (No specific test framework identified in the codebase)

# Linting (no specific linter configured)
# Manual code review recommended

# Build/Package (no specific build process identified)
```

### Utilities

```bash
# Generate Pyrogram session string (interactive)
cd TG-Content-Bot-Pro
python3 get_session.py

# Initialize database
cd TG-Content-Bot-Pro
python3 init_database.py

# Run installation script
cd TG-Content-Bot-Pro
bash install.sh

# Test proxy configuration
cd TG-Content-Bot-Pro
python3 test_proxy.py
```

### Bot User Commands

- `/start` - Initialize bot, show personal stats
- `/batch` - Batch download messages (owner only, max 100)
- `/cancel` - Cancel ongoing batch operation (owner only)
- `/traffic` - View personal traffic statistics (daily/monthly/total)
- `/stats` - View bot statistics (owner only)
- `/history` - View recent 20 downloads (owner only)
- `/queue` - View queue and rate limiter status (owner only)
- `/totaltraffic` - View total traffic statistics (owner only)
- `/setlimit` - Configure traffic limits (owner only)
- `/resettraffic` - Reset traffic statistics (owner only)
- `/addsession` - Add user SESSION via MongoDB (owner only)
- `/delsession` - Delete user SESSION (owner only)
- `/sessions` - List all stored SESSIONs (owner only)
- `/mysession` - View own SESSION string
- `/generatesession` - Online SESSION generation (owner only)
- `/cancelsession` - Cancel SESSION generation (owner only)

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug logging
LOG_LEVEL=DEBUG python3 -m main

# Run tests (if available)
# (No specific test framework identified in the codebase)

# Linting (no specific linter configured)
# Manual code review recommended

# Build/Package (no specific build process identified)
```

### Bot User Commands

- `/start` - Initialize bot, show personal stats
- `/batch` - Batch download messages (owner only, max 100)
- `/cancel` - Cancel ongoing batch operation (owner only)
- `/traffic` - View personal traffic statistics (daily/monthly/total)
- `/stats` - View bot statistics (owner only)
- `/history` - View recent 20 downloads (owner only)
- `/queue` - View queue and rate limiter status (owner only)
- `/totaltraffic` - View total traffic statistics (owner only)
- `/setlimit` - Configure traffic limits (owner only)
- `/resettraffic` - Reset traffic statistics (owner only)
- `/addsession` - Add user SESSION via MongoDB (owner only)
- `/delsession` - Delete user SESSION (owner only)
- `/sessions` - List all stored SESSIONs (owner only)
- `/mysession` - View own SESSION string
- `/generatesession` - Online SESSION generation (owner only)
- `/cancelsession` - Cancel SESSION generation (owner only)

## Architecture

### Triple Client System

The bot operates with THREE Telegram clients simultaneously (`main/core/clients.py`):

1. **bot** (Telethon) - Main bot client for event handling and large file uploads
2. **userbot** (Pyrogram) - User session client for accessing restricted channels
3. **pyrogram_bot** (Pyrogram) - Secondary bot client for Pyrogram-specific operations

This dual-library approach exists because:
- Telethon is used for event handling and large file uploads via `fast_upload`
- Pyrogram is used for accessing restricted content through user sessions
- Both are initialized with credentials from environment variables

### Core Application Flow

The application follows this startup sequence:
1. Environment variables are loaded from `.env` file or system environment
2. Database connection is established via `main/core/database.py`
3. Telegram clients are initialized in `main/core/clients.py`
4. Task queue and rate limiter are started (`main/core/task_queue.py`, `main/core/rate_limiter.py`)
5. Plugins are dynamically loaded from `main/plugins/` directory
6. Event handlers are registered with the Telethon client
7. The bot begins listening for messages

### Plugin System

Plugins auto-load from `main/plugins/` directory:
- `main/__main__.py` uses glob to discover all `.py` files
- `main/core/plugin_manager.py` dynamically imports each plugin
- Plugins register event handlers using decorators from Telethon/Pyrogram

Key plugin files:
- `message_handler.py` - Handles message link processing
- `batch.py` - Implements batch download functionality
- `auth_commands.py` - Authentication-related commands
- `traffic_commands.py` - Traffic monitoring commands
- `session_commands.py` - Session management commands

### Core Message Flow

1. User sends message link → `message_handler.py` processes the request
2. Link parsing → `utils/media_utils.py:get_link()` extracts chat_id and msg_id
3. Message retrieval → `services/download_service.py:download_message()` downloads from source channel
4. Traffic check → `services/traffic_service.py:check_traffic_limit()` validates user quota
5. Upload to user → Uses Pyrogram or Telethon depending on media type/size
6. Cleanup → Downloaded files are removed after upload

### File Upload Strategy (`main/services/download_service.py`)

Implements fallback logic:
- Tries Pyrogram upload first
- Falls back to Telethon's `fast_upload` for large files or errors
- Different handling for video notes, videos, photos, documents
- Automatic metadata extraction using ethon library

### Database Systems

**MongoDB Database (`main/core/database.py`)** - Required for all data storage:
- **users**: user_id, username, is_banned, join_date, last_used
- **download_history**: message_id, chat_id, media_type, file_size, status
- **user_stats**: total_downloads, total_size per user
- **batch_tasks**: batch operations with progress tracking
- **user_traffic**: daily/monthly/total upload/download statistics
- **traffic_limits**: global traffic limit configuration
- **settings**: traffic limit configuration
- **sessions**: encrypted user session storage

### Task Queue & Rate Limiting (`main/services/download_task_manager.py`, `main/core/rate_limiter.py`)

Three-component system:
1. **TaskQueue**: Async queue with configurable concurrent workers for parallel processing
2. **RateLimiter**: Token bucket algorithm for smooth rate control
3. **AdaptiveRateLimiter**: Auto-adjusts rate based on Telegram responses
   - Initial rate: 0.5 requests/sec
   - Range: 0.1 - 10 requests/sec
   - Burst: 3 tokens
   - On FloodWait: reduces rate by 50%
   - After 10 consecutive successes: increases rate by 20%

### Message Link Formats

Supports (`utils/media_utils.py`):
- Public channels: `t.me/channel/msgid`
- Private channels: `t.me/c/chatid/msgid`
- Bot channels: `t.me/b/chatid/msgid`
- Handles `?single` parameter removal
- Chat ID conversion for private channels: `-100` prefix

### Proxy Configuration

The bot supports both SOCKS5 and HTTP proxies with optional authentication:

1. **SOCKS5 Proxy**:
   ```bash
   TELEGRAM_PROXY_SCHEME=socks5
   TELEGRAM_PROXY_HOST=your-proxy-server.com
   TELEGRAM_PROXY_PORT=1080
   # Optional authentication
   TELEGRAM_PROXY_USERNAME=your_username
   TELEGRAM_PROXY_PASSWORD=your_password
   ```

2. **HTTP Proxy**:
   ```bash
   TELEGRAM_PROXY_SCHEME=http
   TELEGRAM_PROXY_HOST=your-proxy-server.com
   TELEGRAM_PROXY_PORT=8080
   # Optional authentication
   TELEGRAM_PROXY_USERNAME=your_username
   TELEGRAM_PROXY_PASSWORD=your_password
   ```

For more detailed proxy configuration instructions, see `PROXY_CONFIGURATION.md` or `SOCKS5_PROXY_SOLUTION.md`.

### Plugin System

Plugins auto-load from `main/plugins/` directory:
- `main/__main__.py` uses glob to discover all `.py` files
- `main/core/plugin_manager.py` dynamically imports each plugin
- Plugins register event handlers using decorators from Telethon/Pyrogram

Key plugin files:
- `message_handler.py` - Handles message link processing
- `batch.py` - Implements batch download functionality
- `auth_commands.py` - Authentication-related commands
- `traffic_commands.py` - Traffic monitoring commands
- `session_commands.py` - Session management commands

### Core Message Flow

1. User sends message link → `message_handler.py` processes the request
2. Link parsing → `utils/media_utils.py:get_link()` extracts chat_id and msg_id
3. Message retrieval → `services/download_service.py:download_message()` downloads from source channel
4. Traffic check → `services/traffic_service.py:check_traffic_limit()` validates user quota
5. Upload to user → Uses Pyrogram or Telethon depending on media type/size
6. Cleanup → Downloaded files are removed after upload

### File Upload Strategy (`main/services/download_service.py`)

Implements fallback logic:
- Tries Pyrogram upload first
- Falls back to Telethon's `fast_upload` for large files or errors
- Different handling for video notes, videos, photos, documents
- Automatic metadata extraction using ethon library

### Database Systems

**MongoDB Database (`main/core/database.py`)** - Required for all data storage:
- **users**: user_id, username, is_banned, join_date, last_used
- **download_history**: message_id, chat_id, media_type, file_size, status
- **user_stats**: total_downloads, total_size per user
- **batch_tasks**: batch operations with progress tracking
- **user_traffic**: daily/monthly/total upload/download statistics
- **traffic_limits**: global traffic limit configuration
- **settings**: traffic limit configuration
- **sessions**: encrypted user session storage

### Task Queue & Rate Limiting (`main/services/download_task_manager.py`, `main/core/rate_limiter.py`)

Three-component system:
1. **TaskQueue**: Async queue with configurable concurrent workers for parallel processing
2. **RateLimiter**: Token bucket algorithm for smooth rate control
3. **AdaptiveRateLimiter**: Auto-adjusts rate based on Telegram responses
   - Initial rate: 0.5 requests/sec
   - Range: 0.1 - 10 requests/sec
   - Burst: 3 tokens
   - On FloodWait: reduces rate by 50%
   - After 10 consecutive successes: increases rate by 20%

### Message Link Formats

Supports (`utils/media_utils.py`):
- Public channels: `t.me/channel/msgid`
- Private channels: `t.me/c/chatid/msgid`
- Bot channels: `t.me/b/chatid/msgid`
- Handles `?single` parameter removal
- Chat ID conversion for private channels: `-100` prefix

### Proxy Configuration

The bot supports both SOCKS5 and HTTP proxies with optional authentication:

1. **SOCKS5 Proxy**:
   ```bash
   TELEGRAM_PROXY_SCHEME=socks5
   TELEGRAM_PROXY_HOST=your-proxy-server.com
   TELEGRAM_PROXY_PORT=1080
   # Optional authentication
   TELEGRAM_PROXY_USERNAME=your_username
   TELEGRAM_PROXY_PASSWORD=your_password
   ```

2. **HTTP Proxy**:
   ```bash
   TELEGRAM_PROXY_SCHEME=http
   TELEGRAM_PROXY_HOST=your-proxy-server.com
   TELEGRAM_PROXY_PORT=8080
   # Optional authentication
   TELEGRAM_PROXY_USERNAME=your_username
   TELEGRAM_PROXY_PASSWORD=your_password
   ```

For more detailed proxy configuration instructions, see `PROXY_CONFIGURATION.md` or `SOCKS5_PROXY_SOLUTION.md`.

## Environment Variables

Required in `.env` (see `.env.example`):
- `API_ID`, `API_HASH` - Telegram API credentials from my.telegram.org
- `BOT_TOKEN` - Bot token from @BotFather
- `SESSION` - Pyrogram session string (generate with `python3 get_session.py`)
- `AUTH` - Owner user ID (integer)
- `FORCESUB` - Optional channel username for forced subscription
- `MONGO_DB` - MongoDB connection string for SESSION management and all data storage
- `ENCRYPTION_KEY` - Encryption key for SESSION storage (auto-generated if not provided)

Optional environment variables:
- `MAX_WORKERS` - Number of concurrent download workers (default: 3)
- `CHUNK_SIZE` - Download chunk size in bytes (default: 1MB)
- `DEFAULT_DAILY_LIMIT` - Daily traffic limit in bytes (default: 1GB)
- `DEFAULT_MONTHLY_LIMIT` - Monthly traffic limit in bytes (default: 10GB)
- `DEFAULT_PER_FILE_LIMIT` - Per-file size limit in bytes (default: 100MB)
- `DEBUG` - Enable debug logging (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)
- `TELEGRAM_PROXY_USERNAME` - Proxy username for authenticated proxies
- `TELEGRAM_PROXY_PASSWORD` - Proxy password for authenticated proxies

### Configuration Management

The application uses `python-decouple` for configuration management via `main/config.py`. Configuration values are validated at startup and the application will fail to start if required values are missing.

## Key Implementation Details

### Traffic Management

Default limits (configurable via `/setlimit`):
- Daily limit: 1GB per user
- Monthly limit: 10GB per user
- Single file limit: 100MB
- Enabled by default

Traffic is checked before each download (`services/download_service.py`):
- Gets file size from message metadata
- Calls `traffic_service.check_traffic_limit(sender, file_size)`
- Rejects download if over quota with informative message
- Records traffic on successful upload

Traffic limits are stored in MongoDB and can be dynamically adjusted without restarting the application.

### Batch Downloads (`main/plugins/batch.py`)

- Maximum 100 messages per batch
- Uses adaptive rate limiting instead of fixed delays
- Progress updates every 5 messages
- Tracks success/failed counts separately
- Database persistence for task recovery
- Performance: 3-10 minutes for 100 messages

### SESSION Management

Two modes:
1. **Environment Variable**: Set `SESSION` in `.env` file
2. **MongoDB Dynamic**: Use `/addsession` command to store SESSIONs per user

MongoDB mode allows:
- Multiple users to have their own SESSION
- Runtime SESSION updates without restart
- Session encryption and secure storage

### Error Handling

Comprehensive handling for:
- Channel access errors (ChannelBanned, ChannelPrivate, etc.)
- FloodWait with automatic retry and adaptive rate reduction
- File upload failures with Telethon fallback
- PeerIdInvalid with link format conversion
- Missing SESSION with helpful error messages

The application uses custom exception classes defined in `main/exceptions/` for structured error handling.

### Batch Downloads (`main/plugins/batch.py`)

- Maximum 100 messages per batch
- Uses adaptive rate limiting instead of fixed delays
- Progress updates every 5 messages
- Tracks success/failed counts separately
- Database persistence for task recovery
- Performance: 3-10 minutes for 100 messages

### SESSION Management

Two modes:
1. **Environment Variable**: Set `SESSION` in `.env` file
2. **MongoDB Dynamic**: Use `/addsession` command to store SESSIONs per user

MongoDB mode allows:
- Multiple users to have their own SESSION
- Runtime SESSION updates without restart
- Session encryption and secure storage

### Error Handling

Comprehensive handling for:
- Channel access errors (ChannelBanned, ChannelPrivate, etc.)
- FloodWait with automatic retry and adaptive rate reduction
- File upload failures with Telethon fallback
- PeerIdInvalid with link format conversion
- Missing SESSION with helpful error messages

## Dependencies

Core libraries (`requirements.txt`):
- Custom Telethon fork: `github.com/vasusen-code/Telethon/archive/refs/tags/v1.24.0.zip`
- Custom ethon fork: `github.com/vasusen-code/ethon/archive/refs/tags/v0.1.5.zip`
- pyrogram - User session management
- python-decouple - Environment variable handling
- cryptg, tgcrypto - Crypto acceleration
- pymongo, dnspython - MongoDB support
- cryptography - Session encryption
- nest_asyncio - Asyncio nesting support

System dependency: **ffmpeg** (required for video processing and metadata extraction)

### Core Components

1. **Telegram Clients**: Telethon and Pyrogram for different operations
2. **Database**: MongoDB for all persistent storage
3. **Task Queue**: Custom asyncio-based queue system for download management
4. **Rate Limiter**: Adaptive rate limiting to prevent FloodWait errors
5. **Plugin System**: Dynamic loading of command handlers and features
6. **Configuration**: Environment-based configuration with validation

## Development Guidelines

### Code Structure

```
main/
├── __main__.py          # Application entry point
├── app.py               # Main application logic
├── config.py            # Configuration management
├── core/                # Core components
│   ├── clients.py       # Telegram client management
│   ├── database.py      # Database operations
│   ├── plugin_manager.py # Plugin loading system
│   ├── base_plugin.py   # Base plugin class
│   ├── task_queue.py    # Task queue management
│   └── rate_limiter.py  # Rate limiting
├── plugins/             # Bot command plugins
│   ├── message_handler.py # Message link processing
│   ├── batch.py         # Batch download functionality
│   ├── auth_commands.py # Authentication commands
│   └── ...              # Other command handlers
├── services/            # Business logic services
├── utils/               # Utility functions
└── exceptions/          # Custom exception classes
```

### Adding New Features

1. Create a new plugin in `main/plugins/` directory
2. Register event handlers using Telethon/Pyrogram decorators
3. Add any required database collections to `main/core/database.py`
4. Update this AGENTS.md file with new commands or functionality

### Plugin Development

All plugins should inherit from `BasePlugin` in `main/core/base_plugin.py` and implement the required abstract methods:
- `on_load()` - Called when plugin is loaded
- `on_unload()` - Called when plugin is unloaded

Plugins have access to core services through injected properties:
- `self.clients` - Telegram client manager
- `self.users` - User service
- `self.sessions` - Session service
- `self.traffic` - Traffic service
- `self.downloads` - Download service

### Security Considerations

- All SESSION strings are encrypted before storage in MongoDB
- Sensitive data is masked in logs
- Access control is implemented for owner-only commands
- Traffic limits prevent abuse
- Input validation is performed on all user inputs

### Error Handling

The application uses a structured exception hierarchy:
- `BaseBotException` - Base exception class
- `TelegramException` - Telegram-related errors
- `ValidationException` - Input validation errors
- `ConfigurationException` - Configuration errors

All services and plugins should use appropriate exception types and handle errors gracefully.

### Adding New Features

1. Create a new plugin in `main/plugins/` directory
2. Register event handlers using Telethon/Pyrogram decorators
3. Add any required database collections to `main/core/database.py`
4. Update this AGENTS.md file with new commands or functionality

### Security Considerations

- All SESSION strings are encrypted before storage in MongoDB
- Sensitive data is masked in logs
- Access control is implemented for owner-only commands
- Traffic limits prevent abuse
- Input validation is performed on all user inputs

## Important Notes

- The bot requires both API credentials AND a user session string
- User session must have access to channels being cloned
- Session file `bot.session` is auto-generated by Telethon
- All Chinese text is intentional - bot has full Chinese interface
- Traffic statistics stored in MongoDB (no SQLite support)
- MongoDB is required for all functionality including SESSION management
- Without SESSION, bot can only access public channels

### Concurrency Model

The application uses asyncio for concurrency with:
- Multiple worker threads for download tasks
- Rate limiting to prevent API throttling
- Asynchronous database operations
- Non-blocking I/O operations where possible

### Logging

The application uses Python's built-in logging module with configurable levels. In production, use `LOG_LEVEL=INFO` and in development use `LOG_LEVEL=DEBUG` for more detailed output.