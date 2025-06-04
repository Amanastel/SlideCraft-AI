# API Reference - SlideCraft AI

This document provides detailed API reference for all endpoints in the SlideCraft AI platform.

## Base URL
```
http://localhost:8086
```

## Authentication
Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Endpoints

### 1. Health Check
**GET** `/`

Returns a simple health check message.

**Response:**
```
200 OK
"Hello, this is the LangChain Google Gemini 1.5 Flash API for generating slides!"
```

---

### 2. Initiate Slide Generation
**POST** `/api/v1/slides/initiate`

Creates a new slide generation request and returns a tracking ID.

**Request Body:**
```json
{
  "input": {
    "id": 12345,
    "title": "Presentation Title",
    "theme": "light", // or "dark"
    "outline": [
      {
        "id": 1,
        "title": "Section Title",
        "points": [
          "Key point 1",
          "Key point 2",
          "Key point 3"
        ]
      }
    ]
  }
}
```

**Response:**
```json
{
  "request_id": "uuid-string"
}
```

---

### 3. Generate Slides (BAML-based)
**GET** `/api/v1/slides/generate?id={request_id}`

Generates slides using the BAML client system. Returns cached results if available.

**Parameters:**
- `id` (required): Request ID from initiate endpoint

**Response:**
```json
{
  "cached": false,
  "data": {
    "slides": [
      {
        "slide_id": "slide_001",
        "background": "linear-gradient(135deg, #ffffff, #f0f4f8)",
        "content": [
          {
            "id": "content_001",
            "type": "heading",
            "x": 50,
            "y": 100,
            "width": 800,
            "height": 80,
            "content": "Slide Title",
            "style": {
              "font_family": "Montserrat",
              "font_size": "46px",
              "color": "#2c3e50"
            }
          }
        ]
      }
    ]
  }
}
```

---

### 4. Generate Slides (Template-based)
**GET** `/api/v1/slides/generate-2?id={request_id}`

Generates slides using the template-based system with Gemini AI.

**Parameters:**
- `id` (required): Request ID from initiate endpoint

**Response:**
```json
{
  "cached": false,
  "data": [
    {
      "slide_id": "slide_001",
      "background": {
        "type": "gradient",
        "value": "linear-gradient(135deg, #ffffff, #f0f4f8)"
      },
      "content": [
        {
          "id": "content_001",
          "type": "heading",
          "text": "Slide Title",
          "style": {
            "fontSize": "46px",
            "fontWeight": "bold",
            "color": "#2c3e50",
            "position": "absolute",
            "left": "7%",
            "top": "8%"
          }
        }
      ]
    }
  ]
}
```

---

### 5. Get Slide Content
**POST** `/api/v1/slides/content`

Retrieves a specific content element from a slide.

**Request Body:**
```json
{
  "request_id": "uuid-string",
  "slide_id": "slide_001",
  "content_id": "content_001"
}
```

**Response:**
```json
{
  "data": {
    "id": "content_001",
    "type": "heading",
    "text": "Slide Title",
    "style": {
      "fontSize": "46px",
      "fontWeight": "bold",
      "color": "#2c3e50"
    }
  }
}
```

---

### 6. Edit Text Content
**POST** `/api/v1/slides/content/edit-text`

Updates text-based content in a slide using AI generation.

**Request Body:**
```json
{
  "request_id": "uuid-string",
  "slide_id": "slide_001",
  "content_id": "content_001",
  "prompt": "Make this title more engaging and focused on AI technology"
}
```

**Response:**
```json
{
  "message": "Content updated successfully",
  "data": {
    "id": "content_001",
    "type": "heading",
    "text": "AI-Powered Innovation: Transforming Business Excellence",
    "style": {
      "fontSize": "46px",
      "fontWeight": "bold",
      "color": "#2c3e50"
    }
  }
}
```

**Notes:**
- Only works with text-based content types (heading, paragraph, bullet_list, etc.)
- For image content, use the `/api/v1/slides/content/image` endpoint

---

### 7. Generate Image for Content
**POST** `/api/v1/slides/content/image`

Generates an AI image for a specific image content block.

**Request Body:**
```json
{
  "request_id": "uuid-string",
  "slide_id": "slide_001",
  "content_id": "image_content_001"
}
```

**Response:**
```json
{
  "data": {
    "id": "image_content_001",
    "type": "image",
    "src": "https://s3.ap-south-1.amazonaws.com/bucket/images/uuid.png",
    "caption": "AI-generated visualization",
    "prompt": "3D visualization of AI technology...",
    "is_image_created": true
  }
}
```

---

### 8. Generate All Images
**POST** `/api/v1/slides/generate-all-images`

Generates images for all image content blocks in a presentation (asynchronous).

**Request Body:**
```json
{
  "request_id": "uuid-string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Image generation started"
}
```

**Note:** This endpoint starts asynchronous processing and returns immediately.

---

### 9. Generate Single Image
**POST** `/api/v1/images/generate`

Generates a single image from a text prompt and returns base64 data.

**Request Body:**
```json
{
  "prompt": "Modern office environment with AI technology displays"
}
```

**Response:**
```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

### 10. Legacy Image Generation
**POST** `/generate-slide-images`

Legacy endpoint for updating slide JSON with generated images.

**Request Body:**
```json
{
  "data": {
    "slides": [...]
  }
}
```

---

## Error Responses

All endpoints return appropriate HTTP status codes with error messages:

```json
{
  "error": "Error description"
}
```

Common status codes:
- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Content Types

### Supported Content Types
- `heading`: Main slide titles
- `subheading`: Section headers
- `paragraph`: Body text
- `bullet_list`: Bulleted lists
- `numbered_list`: Numbered lists
- `image`: Images with AI generation support
- `table`: Data tables
- `chart`: Charts and graphs
- `quote`: Quoted text
- `callout_box`: Highlighted information
- `statistic`: Key statistics
- `process_flow`: Process diagrams

### Style Properties
Each content element can have style properties:
- `fontSize`: Font size (e.g., "24px")
- `fontWeight`: Font weight (e.g., "bold", "normal")
- `color`: Text color (hex or RGB)
- `position`: "absolute" for precise positioning
- `left`, `top`: Position coordinates
- `width`, `height`: Element dimensions
- `textAlign`: Text alignment
- `lineHeight`: Line spacing

## Theme Support

### Light Theme
- Backgrounds: White, off-white, light gradients
- Text: Dark colors for contrast
- Accents: Soft blues, greens, teals

### Dark Theme  
- Backgrounds: Dark colors, rich gradients
- Text: Light colors for contrast
- Accents: Vibrant colors, purples, cyans

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing:
- Request rate limits per client
- Concurrent generation limits
- Image generation quotas

## Best Practices

1. **Always check for cached results** before generating new slides
2. **Use specific prompts** for content editing to get better results
3. **Generate images asynchronously** for large presentations
4. **Validate input data** before sending requests
5. **Handle errors gracefully** in client applications
