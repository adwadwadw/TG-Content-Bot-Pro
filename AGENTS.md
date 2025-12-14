# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

This is a Telegram bot application called "TG消息提取器 (SaveRestrictedContentBot)" that allows users to save content from public and private Telegram channels. The bot supports features like traffic monitoring, batch forwarding, custom thumbnails, and adaptive rate limiting.

## Code Architecture

### Core Components

1. **Three-Client System**:
   - `bot` (Telethon) - Main robot client for event processing and message forwarding
   - `userbot` (Pyrogram) - User session client for accessing restricted channels
   - `Bot` (Pyrogram) - Auxiliary robot client for Pyrogram-specific operations

2. **Plugin Architecture**:
   - Plugins are automatically loaded from `main/plugins/` directory
   - Uses Telethon/Pyrogram decorators to register event handlers
   - Plugin system enables modular functionality

3. **Database Layer**:
   - MongoDB-based storage for users, message history, batch tasks, and traffic statistics
   - Key collections: users, message_history, batch_tasks, user_traffic, traffic_limits

4. **Service Layer**:
   - Modular services for user management, session handling, permissions, traffic control
   - Services abstract database operations and business logic

5. **Core Systems**:
   - Task queue and rate limiting with adaptive algorithms
   - Session management for user authentication
   - Traffic monitoring and enforcement

### Key Directories

- `main/` - Core application code
- `main/core/` - Core systems (clients, database, plugin manager)
- `main/plugins/` - Feature modules (start, batch, session, traffic commands)
- `main/services/` - Business logic services
- `main/utils/` - Utility functions and helpers

## Development Commands

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Telegram API credentials and MongoDB connection
```

### Running the Application

```bash
# Start the bot
./start.sh

# Or run directly with Python
python3 -m main
```

### Deployment

```bash
# One-click deployment (recommended)
./deploy.sh

# Docker deployment
docker-compose up -d

# Manual deployment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m main
```

### Testing

```bash
# Run tests (if available)
python3 -m pytest tests/

# Run specific test files
python3 comprehensive_test.py
python3 db_test.py
```

## Common Development Tasks

### Adding New Features

1. Create a new plugin in `main/plugins/`
2. Extend existing services in `main/services/`
3. Add new database models in `main/core/database.py`
4. Register event handlers in the plugin's `on_load()` method

### Modifying Configuration

1. Update `main/config.py` for new configuration options
2. Add environment variables to `.env.example`
3. Update validation logic in `_validate_settings()`

### Working with Database Models

1. Modify collections and indexes in `main/core/database.py`
2. Update service methods in corresponding files in `main/services/`
3. Ensure proper error handling and validation

### Extending Plugin Functionality

1. Follow the pattern in existing plugins like `main/plugins/start.py`
2. Register event handlers in `on_load()` method
3. Implement cleanup in `on_unload()` method
4. Use dependency injection for services

## Important Notes

- The application uses both Telethon and Pyrogram clients simultaneously
- MongoDB is required for all data storage operations
- Sessions are critical for accessing private channels
- Rate limiting is implemented to prevent Telegram API throttling
- Traffic monitoring enforces daily/monthly limits per user