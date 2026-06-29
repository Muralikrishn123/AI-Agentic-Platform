# ✅ Requirements & Setup Guide

This document lists **everything** you need to install, configure, and run the Agentic AI Platform from scratch. Read every section carefully before starting.

---

## 1. System Requirements

| Requirement | Minimum Version | Notes |
|---|---|---|
| **Operating System** | Windows 10 / macOS 12 / Ubuntu 20.04 | Any modern OS works |
| **Python** | 3.9+ (tested on 3.14) | Must be added to system `PATH` |
| **Node.js** | 18.0+ | Required for the React frontend |
| **npm** | 8.0+ | Comes bundled with Node.js |
| **Web Browser** | Chrome / Edge (latest) | Required for Voice features (Speech API) |
| **Internet Connection** | Required | For MongoDB Atlas + Gemini API calls |

> ⚠️ **Note for Python 3.14 users**: The platform includes built-in patches for Python 3.14 compatibility with `google-protobuf` and `grpc`. No manual workarounds needed.

---

## 2. Required External Accounts & Services

You must create accounts and obtain credentials for the following services **before** running the app:

### 2a. MongoDB Atlas (Free Tier works)
1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and create a free account.
2. Create a new **Cluster** (Free M0 tier is sufficient).
3. Under **Database Access**, create a database user with a username and password.
4. Under **Network Access**, add `0.0.0.0/0` to the IP Access List (allow all IPs).
5. Click **Connect → Drivers** and copy your connection string. It looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxxx.mongodb.net/?appName=Cluster0
   ```
   Replace `<username>` and `<password>` with the credentials you created.

### 2b. Google Gemini API Key
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Click **Create API Key** and copy the key.
3. The free tier provides daily limits. The platform automatically fails over to backup models (`gemini-2.5-flash-lite`, `gemini-2.0-flash`) if limits are hit.

---

## 3. Backend Python Dependencies

All backend packages are listed in `backend/requirements.txt`:

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.109.0 | Web framework for all API routes |
| `uvicorn[standard]` | 0.27.0 | ASGI server to run FastAPI |
| `pymongo` | 4.6.1 | MongoDB sync driver (used by models) |
| `motor` | 3.3.2 | Async MongoDB driver for FastAPI |
| `pydantic` | 2.5.3 | Data validation for API request/response models |
| `pydantic-settings` | 2.1.0 | Loads settings from `.env` file |
| `python-jose[cryptography]` | 3.3.0 | JWT token creation and decoding |
| `passlib[bcrypt]` | 1.7.4 | Password hashing (bcrypt) |
| `python-multipart` | 0.0.6 | Handles form data in API requests |
| `python-dotenv` | 1.0.0 | Loads `.env` file into environment |
| `google-generativeai` | ≥0.7.0 | Google Gemini LLM API client |
| `openai` | 1.10.0 | OpenAI API client (optional, for future use) |
| `httpx` | 0.26.0 | Async HTTP client used internally |
| `bcrypt` | (auto-installed) | Required by passlib for password hashing |

---

## 4. Frontend Node.js Dependencies

All frontend packages are listed in `frontend/package.json`:

| Package | Version | Purpose |
|---|---|---|
| `react` | 18.2.0 | Core UI library |
| `react-dom` | 18.2.0 | DOM rendering for React |
| `react-router-dom` | 6.22.0 | Client-side page routing |
| `axios` | 1.6.7 | HTTP client for API calls to backend |
| `vite` | 5.1.0 | Fast development build tool |
| `@vitejs/plugin-react` | 4.2.1 | Babel/React JSX transform for Vite |
| `autoprefixer` | 10.4.17 | CSS vendor prefix auto-injection |
| `postcss` | 8.4.35 | CSS processing tool |
| `tailwindcss` | 3.4.1 | Utility CSS framework (dev only) |

---

## 5. Environment Variables (`.env` file)

Create a file named exactly `.env` inside the `backend/` folder with the following variables:

```ini
# ── Database ──────────────────────────────────────────────────────────────────
MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxxx.mongodb.net/?appName=Cluster0
DATABASE_NAME=agentic_platform

# ── Security ──────────────────────────────────────────────────────────────────
# Generate a strong random secret key (minimum 32 characters)
SECRET_KEY=your-very-long-secret-key-here-make-it-random-and-secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ── LLM Providers ─────────────────────────────────────────────────────────────
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here   # Optional, not used by default

# ── Application ───────────────────────────────────────────────────────────────
ENVIRONMENT=development
LOG_LEVEL=INFO
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGODB_URL` | ✅ Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | ✅ Yes | `agentic_platform` | Name of the MongoDB database |
| `SECRET_KEY` | ✅ Yes | *(none)* | JWT signing secret — **must be set** |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Session duration in minutes |
| `GEMINI_API_KEY` | ✅ Yes | *(none)* | Google Gemini API key for LLM calls |
| `OPENAI_API_KEY` | No | *(none)* | OpenAI key (not used by default) |
| `ENVIRONMENT` | No | `development` | App environment flag |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## 6. Network Ports Used

| Service | Port | URL |
|---|---|---|
| Backend (FastAPI) | **8001** | `http://localhost:8001` |
| Frontend (Vite) | **5173** | `http://localhost:5173` |
| API Docs (Swagger) | **8001** | `http://localhost:8001/docs` |
| MongoDB Atlas | Remote | Your Atlas cluster URL |
| Gemini API | Remote | `https://generativelanguage.googleapis.com` |

> The frontend Vite dev server **automatically proxies** all `/api/*` requests to `http://localhost:8001`. You do not need to configure anything extra.

---

## 7. Browser Requirements (for Voice Features)

The Voice Input and Voice Output features use native browser APIs:

| Feature | API Used | Supported Browsers |
|---|---|---|
| 🎤 Voice Input (Speech-to-Text) | `window.webkitSpeechRecognition` | Chrome 33+, Edge 79+ |
| 🔊 Voice Output (Text-to-Speech) | `window.speechSynthesis` | Chrome 33+, Edge 18+, Safari 7+ |

> ⚠️ **Firefox does not support `webkitSpeechRecognition`**. Use Google Chrome or Microsoft Edge for voice features.

---

## 8. Complete Setup Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/Muralikrishn123/AI-Agentic-Platform.git
cd "AI-Agentic-Platform"
```

### Step 2: Set Up the Backend
```bash
# Navigate to backend
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install all Python dependencies
pip install -r requirements.txt

# Create the .env file (copy from example and fill in your values)
copy .env.example .env
# Now open .env and fill in: MONGODB_URL, SECRET_KEY, GEMINI_API_KEY
```

### Step 3: Start the Backend Server
```bash
# Windows (recommended — sets correct encoding)
run_backend.bat

# OR: Manual start
python -m uvicorn app.main:app --port 8001
```
✅ You should see: `INFO: Uvicorn running on http://127.0.0.1:8001`

### Step 4: Set Up the Frontend
```bash
# Open a NEW terminal window
cd frontend

# Install all Node.js packages
npm install
```

### Step 5: Start the Frontend Server
```bash
npm run dev
```
✅ You should see: `Local: http://localhost:5173/`

### Step 6: Open the Application
Open your browser and navigate to:
```
http://localhost:5173
```

---

## 9. Quick Verification Checklist

Before using the app, verify all these are working:

- [ ] Backend health check: Open `http://localhost:8001/api/health` — should return `{"status": "healthy"}`
- [ ] API Docs: Open `http://localhost:8001/docs` — should show Swagger UI
- [ ] Frontend loads: Open `http://localhost:5173` — should show Login page
- [ ] Create an account and log in successfully
- [ ] Go to Dashboard → Start a test workflow
- [ ] Check that the animated pipeline progress appears on the Results page
- [ ] Open the floating chat widget (bottom-right) and ask a question

---

## 10. Common Problems & Fixes

| Problem | Cause | Fix |
|---|---|---|
| `SECRET_KEY not found` | Missing `.env` file or missing `SECRET_KEY` variable | Create `backend/.env` and add `SECRET_KEY=any-long-string` |
| `GEMINI_API_KEY not found` | Missing API key in `.env` | Add `GEMINI_API_KEY=your-key` to `backend/.env` |
| `Cannot connect to MongoDB` | Wrong connection string or IP not whitelisted | Check `MONGODB_URL` in `.env` and add `0.0.0.0/0` in Atlas Network Access |
| `Port 8001 already in use` | Another process is using the port | Run `netstat -ano \| findstr :8001` and kill the process |
| `Port 5173 already in use` | Another Vite process is running | Close the other terminal or run `npm run dev -- --port 5174` |
| `Chatbot returns 500 error` | Gemini API daily quota exceeded | Wait until midnight (quota resets daily) or use a new API key |
| Voice mic not working | Using Firefox | Switch to Chrome or Microsoft Edge |
| `UnicodeEncodeError` in terminal | Windows console encoding | The `run_backend.bat` sets `PYTHONIOENCODING=utf-8` automatically |
