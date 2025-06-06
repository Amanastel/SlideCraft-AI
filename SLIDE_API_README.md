# Slide Edit API

A REST API service for editing PowerPoint slides using AI. This API takes slide data and edit prompts, then returns modified slides with professional styling and layout.

## Features

- ✅ **Single Slide Editing** - Edit individual slides with natural language prompts
- ✅ **Batch Slide Editing** - Edit multiple slides in one request
- ✅ **Theme Support** - Light and dark theme options
- ✅ **Validation** - Built-in validation for slide data and edit results
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **CORS Enabled** - Ready for web frontend integration

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python slide_edit_api.py
```

The server will start on `http://localhost:5000`

### 3. Test the API
```bash
python test_slide_edit_api.py
```

## API Endpoints

### `POST /edit-slide`
Edit a single slide with an AI-powered edit prompt.

**Request Body:**
```json
{
  "slide": {
    "slide_id": "slide_10",
    "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
    "content": [
      {
        "id": "s10_title",
        "type": "html", 
        "x": 120,
        "y": 40,
        "width": 960,
        "height": 60,
        "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Title</h1>"
      }
    ]
  },
  "editPrompt": "Change the title color to blue and make it larger",
  "theme": "light"
}
```

**Response:**
```json
{
  "success": true,
  "editedSlide": {
    "slide_id": "slide_10",
    "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
    "content": [...]
  },
  "originalSlideId": "slide_10",
  "editPrompt": "Change the title color to blue and make it larger",
  "theme": "light"
}
```

### `POST /edit-slides`
Edit multiple slides in batch.

**Request Body:**
```json
{
  "requests": [
    {
      "slide": {...},
      "editPrompt": "...",
      "theme": "light"
    },
    ...
  ]
}
```

### `POST /validate-edit`
Validate that an edit was applied correctly.

### `GET /health`
Health check endpoint.

## Slide Data Format

Your slide data must follow this exact structure:

```json
{
  "slide_id": "string",
  "background": "CSS background value",
  "content": [
    {
      "id": "element_id",
      "type": "html" | "image",
      "x": 0,
      "y": 0, 
      "width": 100,
      "height": 50,
      "html": "HTML content with inline styles"
    }
  ]
}
```

### Element Types

#### HTML Elements
```json
{
  "id": "s1_title",
  "type": "html",
  "x": 120,
  "y": 40,
  "width": 960, 
  "height": 60,
  "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Title</h1>"
}
```

#### Image Elements
```json
{
  "id": "s1_img",
  "type": "image",
  "x": 300,
  "y": 200,
  "width": 400,
  "height": 300,
  "src": "https://placehold.co/400x300",
  "alt": "Description",
  "caption": "Image caption",
  "prompt": "AI generation prompt",
  "style": {
    "borderRadius": "8px",
    "objectFit": "cover",
    "marginBottom": "20px"
  }
}
```

## Edit Prompts

Use natural language to describe the changes you want:

- **Text Changes**: "Change the title to 'New Title'"
- **Color Changes**: "Make the text blue" 
- **Size Changes**: "Make the font larger"
- **Layout Changes**: "Move the text to the right"
- **Theme Changes**: "Apply dark theme"
- **Content Changes**: "Replace the paragraph with information about AI"
- **Image Changes**: "Add an image of a robot on the right side"

## Example Usage with cURL

```bash
curl -X POST http://localhost:5000/edit-slide \
  -H "Content-Type: application/json" \
  -d '{
    "slide": {
      "slide_id": "slide_1",
      "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
      "content": [
        {
          "id": "s1_title",
          "type": "html",
          "x": 120,
          "y": 40,
          "width": 960,
          "height": 60,
          "html": "<h1 style=\"text-align:center;font-size:46px;color:#2c3e50\">Original Title</h1>"
        }
      ]
    },
    "editPrompt": "Change the title color to blue",
    "theme": "light"
  }'
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": "Error description",
  "success": false
}
```

Common error codes:
- `400` - Bad request (invalid data)
- `404` - Endpoint not found
- `405` - Method not allowed
- `500` - Internal server error

## Logging

The API logs all requests and errors for debugging. Check the console output for detailed information about processing.

## Development

### Project Structure
```
├── slide_edit_api.py          # Main API server
├── test_slide_edit_api.py     # Test suite
├── baml_src/slide.baml        # BAML slide editing schema
└── requirements.txt           # Python dependencies
```

### Adding New Features

1. Update the BAML schema in `baml_src/slide.baml`
2. Regenerate the BAML client
3. Add new endpoints to `slide_edit_api.py`
4. Add tests to `test_slide_edit_api.py`

## Troubleshooting

### BAML Client Import Error
```bash
pip install baml-py
# Regenerate BAML client if needed
```

### Port Already in Use
```bash
# Change port in slide_edit_api.py
app.run(port=5001)  # Use different port
```

### CORS Issues
CORS is enabled by default. For production, configure specific origins:
```python
CORS(app, origins=["https://your-frontend.com"])
```
