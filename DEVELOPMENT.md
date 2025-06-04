# Development Guide - SlideCraft AI

This guide helps developers understand the codebase structure, contribute to the project, and extend functionality.

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Flask API      │───▶│   MySQL DB      │
│                 │    │   (slide2.py)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Google Gemini   │    │   AWS S3        │
                       │  AI Service      │    │   (Images)      │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  BAML Client     │
                       │  (AI Orchestration)│
                       └──────────────────┘
```

### Core Components

1. **Flask Application** (`slide2.py`)
   - Main API server
   - Request handling and routing
   - Business logic coordination

2. **Image Service** (`slide_service.py`)
   - Dedicated image generation service
   - S3 integration for storage
   - Gemini AI image generation

3. **BAML Client** (`baml_client/`)
   - Business Automation Markup Language
   - AI model orchestration
   - Type-safe AI interactions

4. **Configuration** (`baml_src/`)
   - BAML configuration files
   - AI model definitions
   - Presentation templates

## 📁 Project Structure

```
AIPlannerExecutor/
├── slide2.py                 # Main Flask application
├── slide_service.py          # Image generation service
├── requirements.txt          # Python dependencies
├── configs.ini              # Configuration file
├── README.md                # Project documentation
├── API_REFERENCE.md         # API documentation
├── DEPLOYMENT.md            # Deployment guide
├── DEVELOPMENT.md           # This file
│
├── baml_client/             # BAML generated client
│   ├── __init__.py
│   ├── sync_client.py       # Synchronous BAML client
│   ├── async_client.py      # Asynchronous BAML client
│   ├── types.py            # Type definitions
│   ├── parser.py           # Response parsing
│   └── ...
│
├── baml_src/               # BAML source files
│   ├── clients.baml        # AI client configurations
│   ├── generators.baml     # Generation logic
│   └── ppt.baml           # Presentation-specific logic
│
└── __pycache__/           # Python cache files
```

## 🔧 Development Environment

### Setting Up Development Environment

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd AIPlannerExecutor
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install development dependencies**
   ```bash
   pip install pytest flask-testing black flake8 mypy
   ```

3. **Set up pre-commit hooks** (optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Code Style Guidelines

#### Python Code Style
- Follow **PEP 8** standards
- Use **Black** for code formatting
- Use **flake8** for linting
- Use **mypy** for type checking

```bash
# Format code
black slide2.py slide_service.py

# Lint code
flake8 slide2.py slide_service.py

# Type check
mypy slide2.py slide_service.py
```

#### Naming Conventions
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **API endpoints**: `/api/v1/resource/action`

## 🧩 Core Components Deep Dive

### 1. Flask Application (`slide2.py`)

#### Key Functions

```python
# Main slide generation using templates
def generate_prompt_templateSlide(data):
    """
    Generates slides using Gemini AI with comprehensive prompts.
    Expands mind map content into detailed presentation slides.
    """

# Database operations
def fetch_request_record(request_id):
    """Fetches mind map and slide data from database."""

def store_slide_json(request_id, slide_json):
    """Stores generated slide JSON in database."""

# Image processing
def upload_image_to_s3(image_data: bytes, filename: str) -> str:
    """Uploads generated images to AWS S3."""
```

#### API Endpoints Structure

```python
# Endpoint pattern
@app.route("/api/v1/resource/action", methods=["POST/GET"])
def endpoint_function():
    try:
        # 1. Validate input
        # 2. Process data
        # 3. Call AI services
        # 4. Store results
        # 5. Return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 2. Image Service (`slide_service.py`)

#### Image Generation Pipeline

```python
def generate_image_for_content(request_id, slide_id, content_id):
    """
    1. Fetch slide data from database
    2. Locate specific content block
    3. Generate image using Gemini AI
    4. Upload to S3
    5. Update database with image URL
    6. Return updated content block
    """
```

### 3. BAML Integration

#### BAML Client Usage
```python
from baml_client.sync_client import b

# Generate slides using BAML
slides = b.GeneratePresentation(presentation_input)
```

#### BAML Configuration
- **Client definitions** in `baml_src/clients.baml`
- **Function definitions** in `baml_src/generators.baml`
- **Presentation logic** in `baml_src/ppt.baml`

## 🎨 Design System Implementation

### Content Type System

```python
# Supported content types
CONTENT_TYPES = [
    "heading", "subheading", "paragraph",
    "bullet_list", "numbered_list",
    "image", "infographic", "table", "chart",
    "quote", "icon", "callout_box", "sidebar",
    "timeline", "comparison", "statistic", "process_flow"
]
```

### Styling System

```python
# Style object structure
style = {
    "fontSize": "24px",
    "fontWeight": "bold",
    "color": "#2c3e50",
    "position": "absolute",
    "left": "10%",
    "top": "20%",
    "width": "80%",
    "lineHeight": "1.6"
}
```

### Theme System

```python
def apply_theme_colors(content, theme):
    """Apply theme-specific colors to content elements."""
    if theme == "light":
        return apply_light_theme(content)
    elif theme == "dark":
        return apply_dark_theme(content)
```

## 🧪 Testing

### Test Structure

```python
# test_api.py
import pytest
from slide2 import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    rv = client.get('/')
    assert b'Hello' in rv.data

def test_slide_generation(client):
    """Test slide generation endpoint."""
    data = {
        "input": {
            "id": 123,
            "title": "Test Presentation",
            "outline": [...]
        }
    }
    rv = client.post('/api/v1/slides/initiate', 
                     json=data,
                     content_type='application/json')
    assert rv.status_code == 200
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=slide2

# Run specific test file
pytest test_api.py

# Run with verbose output
pytest -v
```

## 🔌 Adding New Features

### 1. Adding New Content Types

1. **Update content type list**
   ```python
   # In slide2.py, add to CONTENT_TYPES
   CONTENT_TYPES.append("new_content_type")
   ```

2. **Update prompt template**
   ```python
   # In generate_prompt_templateSlide()
   # Add handling for new content type in the prompt
   ```

3. **Update styling system**
   ```python
   # Add specific styling rules for new content type
   def style_new_content_type(content, theme):
       # Implementation
   ```

### 2. Adding New API Endpoints

```python
@app.route("/api/v1/new-feature", methods=["POST"])
def new_feature_endpoint():
    """
    New feature endpoint documentation.
    
    Request Body:
    {
        "param1": "value1",
        "param2": "value2"
    }
    
    Response:
    {
        "result": "success",
        "data": {...}
    }
    """
    try:
        # Validate input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Process data
        result = process_new_feature(data)
        
        # Return response
        return jsonify({"result": "success", "data": result}), 200
        
    except Exception as e:
        logger.error(f"Error in new_feature_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

### 3. Extending AI Integration

```python
def new_ai_function(prompt, model_type="gemini-1.5-flash"):
    """
    Add new AI functionality.
    
    Args:
        prompt: Input prompt for AI
        model_type: Type of AI model to use
    
    Returns:
        AI-generated response
    """
    model = genai.GenerativeModel(model_name=model_type)
    response = model.generate_content(prompt)
    return response.text.strip()
```

## 🔧 Database Schema Management

### Current Schema

```sql
CREATE TABLE slide_requests (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    mindmap_json LONGTEXT,
    slide_json LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Adding New Tables

```sql
-- Example: User management table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: Analytics table
CREATE TABLE slide_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(255),
    action_type VARCHAR(100),
    metadata JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (request_id) REFERENCES slide_requests(id)
);
```

## 🚀 Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import time

# In-memory cache for frequently accessed data
@lru_cache(maxsize=100)
def get_cached_slide_data(request_id):
    """Cache slide data for faster access."""
    return fetch_request_record(request_id)

# Database query optimization
def fetch_request_record_optimized(request_id):
    """Optimized database query with proper indexing."""
    # Use prepared statements and connection pooling
```

### Asynchronous Processing

```python
from threading import Thread
import asyncio

def async_image_generation(request_id):
    """Run image generation asynchronously."""
    thread = Thread(target=generate_all_images_for_presentation, 
                   args=(request_id,))
    thread.start()
    return thread
```

## 🔍 Debugging

### Logging Setup

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Debug Utilities

```python
def debug_request(func):
    """Decorator to log request details."""
    def wrapper(*args, **kwargs):
        logger.debug(f"Request: {request.method} {request.url}")
        logger.debug(f"Data: {request.get_json()}")
        result = func(*args, **kwargs)
        logger.debug(f"Response: {result}")
        return result
    return wrapper

@app.route("/api/v1/debug-endpoint")
@debug_request
def debug_endpoint():
    # Endpoint implementation
```

## 📝 Contributing Guidelines

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```
3. **Make changes with tests**
4. **Run quality checks**
   ```bash
   black slide2.py
   flake8 slide2.py
   pytest
   ```
5. **Commit with descriptive messages**
   ```bash
   git commit -m "feat: add new content type support"
   ```
6. **Push and create PR**

### Commit Message Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive information in code
- [ ] Error handling is comprehensive
- [ ] Performance impact considered

## 🔒 Security Considerations

### Input Validation

```python
from werkzeug.security import safe_str_cmp
import re

def validate_request_id(request_id):
    """Validate request ID format."""
    if not re.match(r'^[a-f0-9-]{36}$', request_id):
        raise ValueError("Invalid request ID format")

def sanitize_prompt(prompt):
    """Sanitize AI prompts for safety."""
    # Remove potentially harmful content
    # Limit prompt length
    # Validate content
```

### API Security

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/v1/protected")
@limiter.limit("10 per minute")
def protected_endpoint():
    # Protected endpoint implementation
```

This development guide provides the foundation for understanding and contributing to SlideCraft AI. Follow these guidelines for consistent, maintainable code.
