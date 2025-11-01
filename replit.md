# NottyBoy - YTMP3 to Telegram API

## Overview
This is a FastAPI backend application that downloads YouTube videos as MP3 audio files and uploads them to a Telegram channel. It provides an API for programmatic access to this functionality with API key management and caching.

## Project Structure
- `main.py` - FastAPI application entry point with Pyrogram bot integration
- `config.py` - Configuration management (credentials currently hardcoded)
- `logging_.py` - Custom logging setup
- `routers/` - API route handlers
  - `yt_mp3_router.py` - YouTube to MP3 conversion endpoints
  - `admin.py` - Admin endpoints for API key management  
- `services/` - Business logic
  - `downloader.py` - YouTube audio download using yt-dlp
  - `uploader.py` - Telegram file upload using Pyrogram
- `utils/` - Utility modules
  - `auth.py` - API key validation and JWT authentication
  - `keygen.py` - API key generation
  - `scheduler_tasks.py` - Scheduled tasks (daily limit reset)
- `database/` - Database modules
  - `mongo.py` - MongoDB connection and setup

## Technology Stack
- **Backend Framework**: FastAPI 0.120.4
- **Telegram Bot**: Pyrogram 2.0.35
- **Database**: MongoDB (Motor async driver 3.7.1)
- **Media Download**: yt-dlp (latest)
- **Task Scheduling**: APScheduler 3.11.1
- **Authentication**: JWT (python-jose), bcrypt (passlib)
- **Media Processing**: ffmpeg

## Setup & Configuration

### Dependencies
All Python dependencies are defined in `requirements.txt` and have been installed:
- FastAPI, Uvicorn, Pydantic
- Pyrogram, TgCrypto
- Motor (MongoDB async)
- APScheduler
- yt-dlp
- JWT and password hashing libraries

System dependencies:
- ffmpeg (for audio conversion)

### Current Configuration Status
- ✅ Python 3.11 installed
- ✅ All Python packages installed
- ✅ ffmpeg installed
- ✅ MongoDB connection configured
- ✅ Telegram bot credentials configured (hardcoded temporarily)
- ⚠️  Telegram bot has synchronization issues (time sync error)
- ✅ Application starts and runs with bot error handled gracefully

### Running the Application
The application is configured to run via workflow:
```bash
uvicorn main:app --host localhost --port 8000 --reload
```

The API server runs on port 8000.

## API Endpoints

### Public Endpoints
- `GET /health` - Health check endpoint (MongoDB and bot status)
- `GET /ytmp3/{api_key}/{video_id}` - Convert YouTube video to MP3 and get Telegram link

### Admin Endpoints (prefix: `/admin`)
- `POST /admin/login` - Admin login (returns JWT token)
- `POST /admin/create_key` - Create new API key (requires admin auth)
- `GET /admin/list_keys` - List all API keys (requires admin auth)
- `POST /admin/reset_limits` - Reset daily usage limits (requires admin auth)

## Features
- YouTube audio download with yt-dlp
- Automatic upload to Telegram channel
- MongoDB caching to avoid reprocessing
- API key-based access control with daily limits
- Admin panel for key management
- Concurrent download limiting (configurable)
- Daily usage reset via scheduler
- Duplicate download prevention with processing locks

## Known Issues
1. **Telegram Bot Time Sync**: The Pyrogram bot encounters time synchronization errors on startup. The application continues to run but bot functionality (file uploads) will not work until this is resolved. This appears to be a system time sync issue between Replit and Telegram's servers.
   - Error: `pyrogram.errors.BadMsgNotification: [16] The msg_id is too low, the client time has to be synchronized`
   - Workaround: Application starts anyway with bot functionality disabled

2. **Security**: Credentials are currently hardcoded in `config.py` for testing. These should be moved to environment variables for production.

## Recent Changes (2025-11-01)
- Fixed package compatibility issues (motor, tgcrypto, passlib versions)
- Renamed `logging.py` to `logging_.py` to avoid conflicts with Python's built-in logging module
- Created `__init__.py` files for proper package imports
- Fixed FastAPI router prefix (removed trailing slash)
- Added error handling for Telegram bot startup to allow app to run even if bot fails
- Installed ffmpeg for audio conversion
- Created .gitignore for Python project

## Next Steps
1. Resolve Telegram bot time synchronization issue
2. Move credentials to environment variables (Replit Secrets)
3. Test API endpoints once bot is connected
4. Add proper error handling and logging throughout
5. Consider adding rate limiting
6. Add API documentation (Swagger/OpenAPI)

## Database Schema
MongoDB collections:
- `api_keys` - API key management with usage tracking
- `audio_cache` - Cached MP3 files with Telegram links
- `processing` - Processing locks to prevent duplicate downloads
