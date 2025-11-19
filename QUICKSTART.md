# Quick Start Guide

Get the LLM Quiz Solver running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- An Anthropic API key ([Get one here](https://console.anthropic.com/))
- Your student email and secret from the Google Form

## Step-by-Step Setup

### 1. Install Dependencies

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your actual values
```

**Required values in .env:**
```env
EMAIL=your-student-email@example.com
SECRET=your-secret-from-google-form
ANTHROPIC_API_KEY=sk-ant-...your-key...
```

### 3. Start the Server

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

**Or manually:**
```bash
python app.py
```

### 4. Verify It's Running

Open another terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Test quiz endpoint (will fail on secret, but shows it's working)
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","secret":"wrong","url":"http://example.com"}'
```

Expected response for wrong secret:
```json
{"error":"Invalid secret"}
```

## Deploy to Internet

For the quiz to work, your endpoint must be accessible from the internet.

### Option 1: ngrok (Easiest for testing)

```bash
# Install ngrok from https://ngrok.com/
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok.io`

Use `https://abc123.ngrok.io/quiz` as your endpoint in the Google Form.

### Option 2: Deploy to Cloud

See the **Deployment** section in README.md for Railway, Render, or Google Cloud Run instructions.

## Troubleshooting

### "Missing required environment variables"
- Check that .env file exists
- Verify all three required variables are set (EMAIL, SECRET, ANTHROPIC_API_KEY)
- No quotes needed around values in .env

### "playwright: command not found"
```bash
playwright install chromium
```

### Port already in use
Change PORT in .env:
```env
PORT=8001
```

### API Key issues
- Get key from: https://console.anthropic.com/
- Format: `sk-ant-...`
- Check billing is enabled

## Testing Locally

Create a test quiz request:

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://example.com/quiz-test"
  }'
```

Check logs in `quiz_solver.log` for detailed information.

## Need Help?

1. Check `quiz_solver.log` for errors
2. Review README.md for detailed documentation
3. Verify all environment variables are correct
4. Test internet connectivity
5. Ensure Claude API key is valid and has credits

## Ready for the Quiz!

Once deployed and tested:
1. Submit your endpoint URL in the Google Form
2. Ensure server is running at quiz time (Sat 29 Nov 2025, 3:00 PM IST)
3. Monitor logs during the quiz
4. The system will automatically solve and submit answers

Good luck!
