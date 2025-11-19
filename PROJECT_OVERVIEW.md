# Project Overview

## What Was Built

A complete end-to-end automated quiz-solving system that:

1. **Receives quiz requests** via REST API
2. **Validates credentials** (email and secret)
3. **Renders JavaScript** quiz pages using headless browser
4. **Analyzes questions** using Claude AI
5. **Processes data** from various sources (PDF, CSV, Excel, JSON)
6. **Performs analysis** (statistical computations, aggregations)
7. **Generates visualizations** (charts, graphs)
8. **Submits answers** in the correct format
9. **Chains through quizzes** automatically

## Core Components

### 1. API Server (`app.py`)
- FastAPI-based REST API
- POST /quiz - Receives quiz requests
- GET /health - Health check endpoint
- GET / - Root endpoint
- Validates JSON payloads (400 on error)
- Validates secrets (403 on invalid)
- Returns 200 and starts async processing

### 2. Quiz Solver (`quiz_solver.py`)
- Main orchestration logic
- Uses Claude AI to:
  - Understand quiz questions
  - Determine solution strategies
  - Compute answers
- Handles quiz chaining
- Implements retry logic
- Manages 3-minute timeout

### 3. Browser Handler (`browser_handler.py`)
- Playwright-based headless browser
- Renders JavaScript pages
- Downloads files
- Takes screenshots for debugging
- Extracts page content and links

### 4. Data Processor (`data_processor.py`)
- PDF parsing with table extraction
- CSV/Excel file reading
- JSON parsing
- Data cleaning and transformation
- Statistical analysis (sum, mean, median, etc.)
- DataFrame operations

### 5. Visualizer (`visualizer.py`)
- Bar charts, line charts, scatter plots
- Histograms, pie charts, heatmaps
- Box plots
- Image generation and base64 encoding

### 6. Configuration (`config.py`)
- Environment variable management
- Settings validation
- Directory creation

## File Structure

```
LLM-Analysis-Quiz/
├── Core Application Files
│   ├── app.py                 # FastAPI server
│   ├── quiz_solver.py         # Main solver logic
│   ├── browser_handler.py     # Browser automation
│   ├── data_processor.py      # Data processing
│   ├── visualizer.py          # Chart generation
│   └── config.py              # Configuration
│
├── Configuration Files
│   ├── .env.example           # Environment template
│   ├── requirements.txt       # Python dependencies
│   └── .gitignore            # Git ignore rules
│
├── Deployment Files
│   ├── Dockerfile            # Docker container
│   ├── docker-compose.yml    # Docker Compose
│   ├── run.sh               # Linux/Mac startup
│   └── run.bat              # Windows startup
│
├── Documentation
│   ├── README.md            # Main documentation
│   ├── QUICKSTART.md        # Quick start guide
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── PROJECT_OVERVIEW.md  # This file
│
├── Testing
│   ├── test_client.py       # API test suite
│   └── test_lab.py          # Legacy test file
│
└── Auto-created Directories
    ├── temp/                # Temporary files
    ├── downloads/           # Downloaded files
    └── quiz_solver.log      # Application logs
```

## Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Browser Automation
- **Playwright** - Headless browser control
- Chromium browser

### AI/ML
- **Anthropic Claude** - Question analysis and solving
- Claude Sonnet 4.5 model

### Data Processing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **PyPDF2** - PDF text extraction
- **pdfplumber** - PDF table extraction
- **openpyxl** - Excel file handling

### Visualization
- **Matplotlib** - Chart generation
- **Seaborn** - Statistical visualization
- **Pillow** - Image processing

### HTTP & Async
- **aiohttp** - Async HTTP client
- **requests** - Sync HTTP client

## How It Works

### Request Flow

```
1. Quiz organizer sends POST to /quiz
   └─> {email, secret, url}

2. API validates request
   ├─> Invalid JSON? → 400
   ├─> Invalid secret? → 403
   └─> Valid → 200, start async processing

3. Quiz Solver orchestrates:
   ├─> Browser visits quiz URL
   ├─> Extracts JavaScript-rendered content
   ├─> Claude analyzes question
   ├─> Downloads any required files
   ├─> Processes data (CSV, PDF, etc.)
   ├─> Performs analysis
   ├─> Generates visualizations if needed
   └─> Formats answer

4. Submit answer to quiz endpoint
   └─> Receive response

5. If there's a next URL:
   └─> Repeat from step 3

6. Continue until:
   ├─> No more URLs
   ├─> Timeout (3 minutes)
   └─> Max retries reached
```

### Example Question Flow

**Question:** "Download [file]. What is the sum of the 'value' column on page 2?"

**Solution:**
1. Browser extracts download link
2. Claude identifies:
   - Task: Data analysis
   - File type: PDF
   - Operation: Sum
   - Target: 'value' column, page 2
3. Download PDF file
4. Extract page 2 tables
5. Parse into DataFrame
6. Compute sum of 'value' column
7. Format as number
8. Submit answer

## Key Features

### Intelligent Question Analysis
- Claude reads and understands questions
- Determines required operations
- Extracts URLs and parameters
- Identifies answer format

### Robust Data Handling
- Multiple file format support
- Automatic type detection
- Data cleaning and validation
- Error recovery

### Flexible Answer Formatting
- Numbers (int/float)
- Strings
- Booleans
- JSON objects
- Base64-encoded images

### Reliability Features
- Retry logic for failed submissions
- Quiz chaining support
- Timeout management
- Comprehensive logging
- Error handling

## Configuration

### Required Environment Variables
```env
EMAIL=your-email@example.com
SECRET=your-secret-key
ANTHROPIC_API_KEY=sk-ant-...
```

### Optional Settings
```env
HOST=0.0.0.0
PORT=8000
CLAUDE_MODEL=claude-sonnet-4-5-20250929
HEADLESS=True
QUIZ_TIMEOUT=180
MAX_RETRIES=2
```

## Testing

### Manual Testing
```bash
# Start server
python app.py

# Run test suite
python test_client.py
```

### Test Suite Includes
- Health check validation
- Invalid JSON handling (400)
- Invalid secret handling (403)
- Valid request processing (200)

## Deployment Options

1. **Local + ngrok** - Quick testing
2. **Railway** - Easy cloud deployment
3. **Render** - Free tier with auto-deploy
4. **Google Cloud Run** - Serverless
5. **Docker** - Portable deployment
6. **AWS EC2** - Full control

See DEPLOYMENT.md for detailed instructions.

## Logging

All operations are logged to:
- Console (stdout)
- `quiz_solver.log` file

Log levels:
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures

## Security

- Secrets stored in .env (not in git)
- Input validation on all endpoints
- Sandboxed browser execution
- No code execution from quiz content
- Rate limiting ready (if needed)

## Performance

- Async operations for non-blocking I/O
- Efficient data processing with pandas
- Headless browser for speed
- Connection pooling
- Optimized for 3-minute deadline

## Limitations & Assumptions

- Requires active internet connection
- Depends on Claude API availability
- 3-minute timeout per quiz chain
- Assumes quiz pages are accessible
- Requires JavaScript rendering capability

## Future Enhancements (Optional)

- [ ] Add rate limiting
- [ ] Implement caching for repeated operations
- [ ] Add metrics/monitoring
- [ ] Support for more file formats
- [ ] ML model integration for predictions
- [ ] Natural language response generation
- [ ] Multi-language support

## Success Criteria

The system successfully:
- ✅ Receives and validates POST requests
- ✅ Returns correct HTTP status codes
- ✅ Renders JavaScript quiz pages
- ✅ Downloads and processes files
- ✅ Performs data analysis
- ✅ Generates visualizations
- ✅ Submits answers in correct format
- ✅ Chains through multiple quizzes
- ✅ Completes within 3-minute timeout
- ✅ Handles errors gracefully
- ✅ Logs all operations

## Support & Troubleshooting

1. Check `quiz_solver.log` for errors
2. Verify environment variables
3. Test with `test_client.py`
4. Review QUICKSTART.md
5. See DEPLOYMENT.md for platform-specific issues
6. Check README.md troubleshooting section

## Credits

Built using:
- FastAPI framework
- Playwright browser automation
- Anthropic Claude AI
- Pandas data analysis
- Matplotlib visualization

Designed for IITM LLM Analysis Quiz evaluation.
