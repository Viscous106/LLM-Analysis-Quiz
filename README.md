# LLM-Analysis-Quiz

An automated quiz-solving system that handles data sourcing, preparation, analysis, and visualization tasks using LLMs (Large Language Models). Built for the IITM LLM Analysis Quiz evaluation.

## Overview

This application:
- Receives quiz requests via POST API endpoint
- Validates student credentials
- Renders JavaScript-based quiz pages using a headless browser
- Analyzes questions using Claude AI
- Downloads and processes data files (PDF, CSV, JSON, Excel)
- Performs data analysis and visualization
- Submits answers automatically within the 3-minute time limit
- Chains through multiple quiz questions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Quiz Request (POST)                      │
│                    /quiz endpoint                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Application                         │
│              (app.py - Secret Validation)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Quiz Solver (quiz_solver.py)               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  1. Browser Handler (browser_handler.py)            │   │
│   │     - Renders JavaScript quiz pages                 │   │
│   │     - Downloads files                               │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  2. Claude API Integration                          │   │
│   │     - Analyzes quiz questions                       │   │
│   │     - Determines solution strategy                  │   │
│   │     - Computes answers                              │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  3. Data Processor (data_processor.py)              │   │
│   │     - PDF, CSV, JSON, Excel parsing                 │   │
│   │     - Data cleaning and transformation              │   │
│   │     - Statistical analysis                          │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  4. Visualizer (visualizer.py)                      │   │
│   │     - Chart generation (bar, line, pie, etc.)       │   │
│   │     - Image creation and encoding                   │   │
│   └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Answer Submission (POST)                        │
│              Returns: {correct, url?, reason?}               │
└─────────────────────────────────────────────────────────────┘
```

## Features

### API Endpoint
- **POST /quiz**: Receives quiz requests with email, secret, and quiz URL
- **GET /**: Health check
- **GET /health**: Detailed health status
- Validates JSON payload (returns 400 if invalid)
- Validates secret (returns 403 if incorrect)
- Returns 200 on valid request and starts async processing

### Quiz Solving Capabilities
- **JavaScript Rendering**: Uses Playwright headless browser to render dynamic quiz pages
- **LLM Analysis**: Claude AI analyzes questions and determines solution strategies
- **Data Processing**:
  - PDF parsing with table extraction
  - CSV, JSON, Excel file handling
  - Data cleaning and transformation
  - Statistical analysis (sum, mean, median, aggregations)
- **Visualization**:
  - Bar charts, line charts, scatter plots
  - Histograms, pie charts, heatmaps
  - Base64 image encoding for submission
- **Smart Submission**:
  - Automatic answer formatting (number, string, boolean, object, base64)
  - Retry logic with improved analysis
  - Quiz chaining (follows next URL if provided)
  - 3-minute timeout enforcement

## Requirements

- Python 3.9+
- Anthropic Claude API key
- Internet connection

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LLM-Analysis-Quiz
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 4. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

Required environment variables:
- `EMAIL`: Your student email address
- `SECRET`: Your secret key (from Google Form submission)
- `ANTHROPIC_API_KEY`: Your Claude API key (get from https://console.anthropic.com/)

### 5. Test the Setup

```bash
# Run the application
python app.py

# In another terminal, test the health endpoint
curl http://localhost:8000/health
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:8000` by default.

### API Endpoints

#### POST /quiz

Receive and process a quiz request.

**Request:**
```json
{
  "email": "student@example.com",
  "secret": "your-secret-key",
  "url": "https://example.com/quiz-834"
}
```

**Success Response (200):**
```json
{
  "status": "accepted",
  "message": "Quiz request accepted and processing started",
  "received_at": "2025-11-29T10:00:00.000Z"
}
```

**Error Responses:**
- 400: Invalid JSON payload
- 403: Invalid secret
- 500: Internal server error

#### GET /health

Check application health status.

**Response:**
```json
{
  "status": "healthy",
  "quiz_solver_ready": true,
  "timestamp": "2025-11-29T10:00:00.000Z"
}
```

### Deployment

#### Local Deployment

For testing locally:

```bash
python app.py
```

#### Production Deployment with ngrok

To expose your local server to the internet:

```bash
# Install ngrok from https://ngrok.com/
# Run ngrok
ngrok http 8000
```

Use the provided HTTPS URL as your API endpoint in the Google Form.

#### Cloud Deployment (Recommended)

Deploy to cloud platforms for better reliability:

**Option 1: Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Option 2: Render**
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt && playwright install chromium`
4. Set start command: `python app.py`
5. Add environment variables in Render dashboard

**Option 3: Google Cloud Run**
```bash
# Install gcloud CLI
gcloud run deploy llm-quiz-solver \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Settings (config.py)

All settings can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| EMAIL | - | Your student email (required) |
| SECRET | - | Your secret key (required) |
| ANTHROPIC_API_KEY | - | Claude API key (required) |
| CLAUDE_MODEL | claude-sonnet-4-5-20250929 | Claude model to use |
| MAX_TOKENS | 8000 | Max tokens for Claude responses |
| HEADLESS | True | Run browser in headless mode |
| BROWSER_TIMEOUT | 30000 | Browser timeout (ms) |
| QUIZ_TIMEOUT | 180 | Quiz solving timeout (seconds) |
| MAX_RETRIES | 2 | Max retry attempts per quiz |

## File Structure

```
LLM-Analysis-Quiz/
├── app.py                    # FastAPI application and endpoints
├── config.py                 # Configuration management
├── quiz_solver.py            # Main quiz solving orchestrator
├── browser_handler.py        # Playwright browser automation
├── data_processor.py         # Data processing utilities
├── visualizer.py             # Visualization utilities
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── LICENSE                   # License file
├── temp/                     # Temporary files (created automatically)
├── downloads/                # Downloaded files (created automatically)
└── quiz_solver.log           # Application logs (created automatically)
```

## Logging

The application logs all activities to:
- `quiz_solver.log` (file)
- Console output

Log levels:
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures and exceptions

## Troubleshooting

### Common Issues

**1. "Missing required environment variables"**
- Ensure .env file exists with EMAIL, SECRET, and ANTHROPIC_API_KEY

**2. "Browser initialization failed"**
- Run `playwright install chromium`
- Check system has sufficient memory

**3. "403 Forbidden on quiz request"**
- Verify SECRET matches what you provided in Google Form
- Check for extra whitespace in .env file

**4. "Timeout errors"**
- Increase QUIZ_TIMEOUT or BROWSER_TIMEOUT in .env
- Check internet connection
- Verify quiz URL is accessible

**5. "Claude API errors"**
- Verify ANTHROPIC_API_KEY is correct
- Check API quota and billing
- Ensure API key has correct permissions

## Test Cases to Pass

The system is designed to handle:

1. **Secret Validation**
   - ✓ Valid secret → 200 response
   - ✓ Invalid secret → 403 response
   - ✓ Invalid JSON → 400 response

2. **Quiz Solving**
   - ✓ JavaScript-rendered pages
   - ✓ File downloads (PDF, CSV, JSON, Excel)
   - ✓ Data extraction from tables
   - ✓ Statistical computations
   - ✓ Visualization generation
   - ✓ Answer submission in correct format

3. **Answer Formats**
   - ✓ Numbers (integer, float)
   - ✓ Strings
   - ✓ Booleans
   - ✓ JSON objects
   - ✓ Base64-encoded images

4. **Quiz Chaining**
   - ✓ Follow next URL on correct answer
   - ✓ Retry on incorrect answer
   - ✓ Skip to next on provided URL
   - ✓ Complete within 3-minute timeout

## Development

### Running Tests

```bash
# Add your test files in tests/ directory
pytest tests/
```

### Adding New Data Processors

Extend `DataProcessor` class in `data_processor.py`:

```python
@staticmethod
def process_new_format(file_path: Path) -> Any:
    # Your implementation
    pass
```

### Adding New Visualizations

Extend `Visualizer` class in `visualizer.py`:

```python
@staticmethod
def create_custom_chart(data, **kwargs) -> Path:
    # Your implementation
    pass
```

## Security Considerations

- Store sensitive credentials in .env (never commit)
- Use HTTPS for production endpoints
- Validate all inputs
- Limit file upload sizes
- Sanitize user data
- Monitor API usage and costs

## Performance Optimization

- Headless browser runs in sandboxed mode
- Async processing for non-blocking operations
- Connection pooling for HTTP requests
- Efficient data processing with pandas
- Caching for repeated operations

## License

See LICENSE file for details.

## Support

For issues and questions:
- Check logs in `quiz_solver.log`
- Review this README
- Check quiz specifications document
- Contact course instructors

## Acknowledgments

- Built with FastAPI, Playwright, and Anthropic Claude
- Uses pandas, matplotlib for data processing
- Supports various data formats for comprehensive analysis
