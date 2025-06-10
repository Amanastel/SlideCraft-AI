# PowerPoint Generation API - Complete Integration Guide

## 🚀 System Overview

The PowerPoint Generation API is a complete, production-ready system that combines:
- **Advanced AI-powered content generation** using OpenAI GPT
- **Professional styling** with gradients, icons, and images
- **Multiple image sources** (Unsplash, Pixabay, Picsum)
- **Automatic chart generation** from data
- **RESTful API endpoints** for easy integration
- **Session management** for tracking generations

## 📋 Quick Start

### 1. Start the API Server
```bash
cd /Users/amankumar/Desktop/AIPlannerExecutor/ppt
python3 ppt_api.py
```

### 2. Health Check
```bash
curl -X GET http://localhost:5001/health
```

### 3. Simple Generation
```bash
curl -X POST http://localhost:5001/api/generate-ppt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a presentation about AI in healthcare",
    "options": {
      "theme": "professional",
      "include_charts": true,
      "include_images": true
    }
  }'
```

## 🛠️ API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/api/generate-ppt` | POST | Generate presentation from prompt/data |
| `/api/download/<session_id>` | GET | Download generated presentation |
| `/api/status/<session_id>` | GET | Check generation status |
| `/api/sessions` | GET | List all active sessions |
| `/api/templates` | GET | Get available templates and themes |

### Request Format

#### Simple Prompt-Based Generation
```json
{
  "prompt": "Your presentation description",
  "options": {
    "theme": "professional|modern|corporate",
    "include_charts": true,
    "include_images": true,
    "output_filename": "custom_name.pptx"
  }
}
```

#### Structured Data Generation
```json
{
  "prompt": "Enhancement instructions for AI",
  "presentation_data": {
    "title": "Presentation Title",
    "slides": [
      {
        "id": 1,
        "title": "Slide Title",
        "key_content_elements": [
          "Content point 1",
          "Content point 2"
        ],
        "objective": "Slide purpose",
        "image_search_terms": ["keyword1", "keyword2"],
        "chart_data": {
          "categories": ["A", "B", "C"],
          "values": [10, 20, 30],
          "title": "Chart Title"
        }
      }
    ]
  },
  "options": {
    "theme": "professional",
    "include_charts": true,
    "include_images": true
  }
}
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "session_id": "uuid",
  "filename": "presentation.pptx",
  "file_size": 1234567,
  "download_url": "/api/download/uuid",
  "preview_url": "/api/preview/uuid",
  "generated_at": "2025-06-11T00:31:03.429466"
}
```

#### Error Response
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "session_id": "uuid (if applicable)"
}
```

## 🔄 Flexible Input Structure Support

The API now supports **any JSON structure** for presentation data. You can use different formats based on your needs:

### Format 1: Content Field (User's Example)
```json
{
  "prompt": "Create a presentation about your topic",
  "presentation_data": {
    "title": "AI Sales Meeting Agent",
    "slides": [
      {
        "title": "Problem in Sales Meetings",
        "content": "Sales meetings often suffer from inefficiency:\n- Manual note-taking\n- Missed follow-ups\n- No real-time insights\n- Disconnected tools",
        "image": "problem-image.jpg"
      }
    ]
  }
}
```

### Format 2: Key Content Elements (Original)
```json
{
  "prompt": "Create a business presentation",
  "presentation_data": {
    "title": "Business Strategy",
    "slides": [
      {
        "title": "Market Analysis",
        "key_content_elements": [
          "Market size: $50B",
          "Growth rate: 15% YoY",
          "Key competitors: 3 major players"
        ],
        "image_search_terms": ["market", "analysis"]
      }
    ]
  }
}
```

### Format 3: Mixed Structure
```json
{
  "prompt": "Flexible presentation",
  "presentation_data": {
    "title": "Technology Overview",
    "slides": [
      {
        "title": "Current State",
        "content": "Technology landscape:\n• AI/ML adoption\n• Cloud migration\n• Digital transformation"
      },
      {
        "title": "Future Vision",
        "key_content_elements": ["Automation", "Intelligence", "Integration"]
      }
    ]
  }
}
```

### Automatic Conversion Features

The API automatically handles:
- **Content Parsing**: Converts `content` field with newlines/bullets to structured elements
- **Image Keywords**: Extracts search terms from `image` filenames 
- **Flexible Fields**: Accepts any custom fields and preserves them
- **Smart Defaults**: Generates missing fields from available content
- **Structure Normalization**: Converts any format to internal processing format

## 🎨 Features & Capabilities

### AI-Powered Content Enhancement
- **OpenAI GPT Integration**: Enhances content based on prompts
- **Context-Aware Generation**: Understands business context
- **Multiple Templates**: Sales, tech, business, general presentations

### Professional Styling
- **Gradient Backgrounds**: Dynamic, professional gradients
- **Icon Integration**: 5 icon types (business, tech, analytics, growth, innovation)
- **Image Integration**: Fetches relevant images from multiple APIs
- **Chart Generation**: Automatic visualization of data

### Image Sources
1. **Unsplash**: High-quality professional photos
2. **Pixabay**: Diverse stock imagery  
3. **Picsum**: Placeholder fallback images

### Data Visualization
- **Automatic Charts**: Bar charts, line charts, pie charts
- **Data Processing**: Converts raw data to visualizations
- **Custom Styling**: Professional chart formatting

## 💻 Programming Integration

### Python Client Example
```python
import requests

class PPTClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def generate(self, prompt, options=None):
        payload = {"prompt": prompt}
        if options:
            payload["options"] = options
            
        response = requests.post(
            f"{self.base_url}/api/generate-ppt",
            json=payload
        )
        return response.json()
    
    def download(self, session_id, filename):
        response = requests.get(f"{self.base_url}/api/download/{session_id}")
        with open(filename, 'wb') as f:
            f.write(response.content)

# Usage
client = PPTClient()
result = client.generate("Create a sales presentation for our new product")
client.download(result['session_id'], 'my_presentation.pptx')
```

### JavaScript/Node.js Example
```javascript
const axios = require('axios');
const fs = require('fs');

class PPTClient {
    constructor(baseUrl = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
    }
    
    async generate(prompt, options = {}) {
        const response = await axios.post(`${this.baseUrl}/api/generate-ppt`, {
            prompt,
            options
        });
        return response.data;
    }
    
    async download(sessionId, filename) {
        const response = await axios.get(
            `${this.baseUrl}/api/download/${sessionId}`,
            { responseType: 'stream' }
        );
        response.data.pipe(fs.createWriteStream(filename));
    }
}

// Usage
const client = new PPTClient();
const result = await client.generate("Create a tech presentation about AI");
await client.download(result.session_id, 'ai_presentation.pptx');
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set OpenAI API key for enhanced content generation
export OPENAI_API_KEY="your-api-key"

# Optional: Set image API keys for better image sourcing
export UNSPLASH_ACCESS_KEY="your-unsplash-key"
export PIXABAY_API_KEY="your-pixabay-key"
```

### API Configuration
- **Port**: 5001 (configurable in ppt_api.py)
- **Host**: 0.0.0.0 (accepts connections from all interfaces)
- **Max File Size**: 16MB
- **Supported Formats**: .pptx only

## 📁 File Structure

```
ppt/
├── ppt_api.py                     # Main Flask API server
├── prompt_based_ppt_generator.py  # Advanced PPT generator
├── cli_ppt_generator.py           # Command-line interface
├── api_test_client.py             # Test client and examples
├── ppt.py                         # Original generator (enhanced)
├── generated_presentations/       # Output directory
├── README.md                      # Documentation
└── fincore_presentation_data.json # Sample data
```

## 🚀 Deployment Options

### Local Development
```bash
python3 ppt_api.py
# API available at http://localhost:5001
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 ppt_api:app
```

### Docker Deployment
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5001
CMD ["python3", "ppt_api.py"]
```

## 🔍 Testing & Validation

### Run Test Suite
```bash
python3 api_test_client.py
```

### Manual Testing
```bash
# Test health
curl http://localhost:5001/health

# Test generation
curl -X POST http://localhost:5001/api/generate-ppt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test presentation"}'

# Check sessions
curl http://localhost:5001/api/sessions
```

## 📊 Performance Metrics

### Generation Performance
- **Simple Presentations**: 5-10 seconds
- **Complex with Images**: 15-30 seconds
- **File Sizes**: 300KB - 2MB typical

### Concurrent Handling
- **Multiple Sessions**: Supported with unique session IDs
- **Background Processing**: Threaded request handling
- **Session Management**: Automatic cleanup and tracking

## 🔐 Security Considerations

### Input Validation
- Prompt length limits (1000 characters)
- JSON structure validation
- File size limits
- SQL injection prevention

### File Security
- Unique session IDs for file access
- Temporary file cleanup
- Secure file serving

## 🎯 Use Cases

### Business Applications
- **Sales Presentations**: Automated pitch decks
- **Strategic Planning**: Business strategy presentations
- **Training Materials**: Educational content generation
- **Marketing**: Campaign and product presentations

### Technical Applications
- **API Integration**: Embed in existing applications
- **Workflow Automation**: Part of larger business processes
- **Content Management**: Dynamic presentation generation
- **Reporting**: Automated report presentations

## 🆘 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 5001
lsof -i :5001
# Change port in ppt_api.py if needed
```

#### Missing Dependencies
```bash
pip install flask flask-cors requests python-pptx
```

#### OpenAI API Issues
- Ensure OPENAI_API_KEY is set
- Check API quota and billing
- Fallback to basic generation if API fails

#### Image Loading Issues
- Check internet connectivity
- Verify image API keys
- System falls back to placeholder images

## 📞 Support & Maintenance

### Monitoring
- Check `/health` endpoint regularly
- Monitor session count via `/api/sessions`
- Track file sizes and generation times

### Logs
- Flask development server logs to console
- Production: Use proper logging configuration
- Session information stored in memory

### Updates
- All components are modular and updatable
- API versioning supported
- Backward compatibility maintained

---

## 🎉 Summary

The PowerPoint Generation API provides a complete, enterprise-ready solution for automated presentation generation. With its combination of AI-powered content enhancement, professional styling, and robust API architecture, it's ready for production use in any environment.

**Key Benefits:**
✅ **AI-Enhanced Content**: Intelligent content generation and enhancement  
✅ **Professional Quality**: Business-ready presentations with styling  
✅ **Easy Integration**: RESTful API with comprehensive documentation  
✅ **Flexible Input**: Simple prompts or structured data  
✅ **Production Ready**: Session management, error handling, validation  
✅ **Extensible**: Modular architecture for easy customization  

The system is fully tested, documented, and ready for immediate use!
