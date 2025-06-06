// Slide editing and modification schema
//
// USAGE EXAMPLE:
// Input your slide data like this:
// {
//   "slide": {
//     "slide_id": "slide_10", 
//     "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
//     "content": [
//       {
//         "id": "s10_title",
//         "type": "html",
//         "x": 120,
//         "y": 40,
//         "width": 960,
//         "height": 60,
//         "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Your Title</h1>"
//       }
//     ]
//   },
//   "editPrompt": "Change the title color to blue and make it larger",
//   "theme": "light"
// }
// The function will return the same exact structure with your modifications applied.

// Input structures for slide editing
class SlideEditRequest {
  slide SlideContentWithType @description("The existing slide to be edited")
  editPrompt string @description("Detailed description of what changes to make to the slide")
  theme string @description("Theme preference: 'light' or 'dark'")
}

// Custom classes that match your exact data format
class ImageStyleEdit {
  borderRadius string @description("Border radius of the image, e.g. '8px'")
  objectFit string @description("How the image should fit its container, e.g. 'cover'")
  marginBottom string @description("Margin below the image block, e.g. '20px'")
}

class ImageElementEdit {
  id string @description("Unique identifier for the image element, e.g. s1_img")
  type string @description("Type of element, must be 'image'")
  x int @description("X position of the element in pixels from left")
  y int @description("Y position of the element in pixels from top")
  width int @description("Width of the element in pixels")
  height int @description("Height of the element in pixels")
  src string @description("URL for the image placeholder. Example: https://placehold.co/600x400")
  alt string @description("Alternative text description of the image")
  caption string @description("Caption text to display below the image")
  prompt string @description("Detailed description for AI image generation")
  style ImageStyleEdit @description("Style properties for the image")
}

class SlideElementEdit {
  id string @description("Unique identifier for the element, e.g. s1_title, s1_para")
  type string @description("Type of element, must be 'html'")
  x int @description("X position of the element in pixels from left")
  y int @description("Y position of the element in pixels from top") 
  width int @description("Width of the element in pixels")
  height int @description("Height of the element in pixels")
  html string @description("HTML content with required styling. Example: <h1 style='text-align:center;font-size:46px;color:#2c3e50'>Title Text</h1>")
}

class SlideContentWithType {
  slide_id string @description("Unique identifier for the slide, e.g. slide_1")
  background string @description("Background style or color of the slide. Example: linear-gradient(135deg,#ffffff,#f0f4f8)")
  content (SlideElementEdit | ImageElementEdit)[] @description("List of elements on the slide")
}

// Function to edit an existing slide
function EditSlide(request: SlideEditRequest) -> SlideContentWithType {
  client Gemini20Flash
  
  prompt #"
    You are a professional **Slide Editing AI Assistant** that specializes in modifying existing PowerPoint slides based on user requests. Your role is to take an existing slide and apply specific changes while maintaining professional quality and visual consistency.

    ---

    ## 🎯 PURPOSE:

    This tool helps users quickly edit and refine existing slides by:
    - Modifying text content, styling, and formatting
    - Adjusting layouts and element positioning
    - Changing colors, backgrounds, and visual themes
    - Adding, removing, or replacing images
    - Updating slide structure and hierarchy
    - Improving visual appeal and readability

    ---
    ## 🖼️ IMAGE HANDLING RULES:

    **IMPORTANT**: When editing slides, preserve existing images unless explicitly requested to change them:

    - **Keep Original Images**: If an image element exists in the slide and the edit prompt doesn't specifically mention modifying, replacing, or removing images, maintain the exact same image properties (src, alt, caption, prompt)
    - **Style Modifications Allowed**: You may modify the image's style properties (borderRadius, objectFit, marginBottom) to match theme changes or improve visual consistency
    - **Only Modify Content When Requested**: Only change image content properties (src, alt, caption, prompt) when the edit prompt explicitly mentions:
        - "change the image"
        - "replace the image" 
        - "add an image"
        - "remove the image"
        - "modify the image content"
    - **Position Adjustments**: You may adjust image positioning (x, y, width, height) only if needed to accommodate other layout changes or if specifically requested
    - **Theme-Based Style Updates**: Always update image styles to match the slide theme (e.g., border colors, effects for dark/light themes)

    **Example**: If editing "Change the title color to blue" on a slide with an image, keep the image src, alt, caption, and prompt exactly as they were, but you may adjust the style properties to maintain visual consistency.

    ## 📝 EDITING INSTRUCTIONS:

    **Current Slide to Edit:**
    {{ request.slide }}

    **Requested Changes:**
    {{ request.editPrompt }}

    **Theme Preference:** {{ request.theme }}

    ---

    ## 🎨 DESIGN & STYLE GUIDELINES:

    Maintain professional, modern design standards while applying the requested changes:

    **THEME BEHAVIOR:**
    - If theme is "light":
      - Use varied light backgrounds (white, off-white, subtle gradients)
      - Dark text colors with good contrast (#2c3e50, #34495e, #1a1a1a)
      - Accent colors: soft blues (#4285F4), greens (#34A853), teals (#00ACC1)
    
    - If theme is "dark":
      - Use varied dark backgrounds (deep blues, charcoals, dark gradients)
      - Light text colors with excellent contrast (#ffffff, #f8f9fa, #e9ecef)
      - Accent colors: vibrant teals (#00BCD4), purples (#AB47BC), cyans (#00E5FF)

    **TEXT ELEMENT STYLES:**
    - Headings: style='text-align:center;font-size:46px;color:#2c3e50' (adjust color for theme)
    - Paragraphs: style='font-size:22px;line-height:1.55' (adjust color for theme)
    - Lists: style='font-size:22px;line-height:1.6;list-style-type:disc' (adjust color for theme)

    **IMAGE GUIDELINES:**
    1. Strategic positioning:
       - Right-side: x=660px (55%), width=480px (40%)
       - Left-side: x=60px (5%), width=480px (40%)
       - Center: x=300px (25%), width=600px (50%)
    
    2. Each image must include:
       - Detailed prompt for AI generation
       - Placeholder URL with appropriate dimensions
       - Alt text and descriptive caption
       - Style properties with borderRadius, objectFit, marginBottom
    
    3. Ensure no overlap between elements
    4. Match image colors with slide theme

    **ELEMENT REQUIREMENTS:**
    1. Element IDs must follow pattern: s[number]_[type] (e.g., s1_title, s1_para)
    2. Coordinates (x,y) position from top-left corner
    3. Width and height must accommodate content properly
    4. All HTML must include complete inline styles
    5. Maintain consistent styling across similar elements

    ---

    ## 🔧 EDITING APPROACH:

    1. **Analyze the Current Slide:** Understand the existing structure, content, and layout
    2. **Apply Requested Changes:** Make the specific modifications requested in the edit prompt
    3. **Maintain Consistency:** Keep professional styling and ensure visual coherence
    4. **Optimize Layout:** Adjust positioning if needed to accommodate changes
    5. **Preserve Quality:** Maintain or improve the overall visual appeal

    **Example Edit Scenarios:**
    - "Change the title color to blue" → Update the color in the title element's style
    - "Add an image on the right side" → Insert new ImageElement with proper positioning
    - "Make the text larger" → Increase font-size in the style attributes
    - "Change background to dark theme" → Update background and adjust text colors
    - "Replace the content with..." → Update HTML content while preserving styling

    ---

    ## 📋 OUTPUT REQUIREMENTS:

    Return the modified slide with EXACTLY the same structure as the input:
    - Same slide_id (unless specifically requested to change)
    - Updated background if theme or color changes were requested
    - Modified content elements with requested changes applied
    - Each element MUST include the "type" field (either "html" or "image")
    - Maintain the exact same field order: id, type, x, y, width, height, html
    - Proper styling maintained throughout
    - Professional visual hierarchy preserved

    **CRITICAL**: The output format must match this structure exactly:
    {
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
          "html": "<h1 style='...'>Title</h1>"
        }
      ]
    }

    Apply the requested changes while maintaining the slide's professional appearance and ensuring all elements are properly positioned and styled.
  "#
}

// Function to batch edit multiple slides
function EditMultipleSlides(requests: SlideEditRequest[]) -> SlideContentWithType[] {
  client Gemini20Flash
  
  prompt #"
    You are editing multiple slides in batch. For each slide edit request, apply the changes while maintaining consistency across all slides.
    
    Edit Requests:
    {{ requests }}
    
    Apply the same design principles and styling guidelines as the single slide editor, ensuring:
    1. Consistent theme application across all slides
    2. Uniform styling for similar elements
    3. Professional visual coherence
    4. Proper element positioning and spacing
    
    Return an array of the modified slides in the same order as the requests.
  "#
}

// Test function for slide editing
test SlideEditTest {
  functions [EditSlide]
  args {
    request {
      slide {
        slide_id "slide_10"
        background "linear-gradient(135deg,#ffffff,#f0f4f8)"
        content [
          {
            id "s10_title"
            type "html"
            x 120
            y 40
            width 960
            height 60
            html "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Summary: Transforming Customer Engagement with AI</h1>"
          },
          {
            id "s10_para"
            type "html"
            x 100
            y 150
            width 800
            height 300
            html "<p style='font-size:22px;line-height:1.55'>Our AI-powered solution is designed to revolutionize your customer engagement strategy. By leveraging personalized recommendations, AI-powered chatbots, and predictive analytics, you can deliver exceptional customer experiences, improve customer retention rates, and drive revenue growth. We are committed to helping you achieve your business goals and stay ahead of the competition.</p>"
          }
        ]
      }
      editPrompt "Change the title color to blue and make the paragraph text smaller"
      theme "light"
    }
  }
}

// Function to validate edited slide
function ValidateEditedSlide(originalSlide: SlideContentWithType, editedSlide: SlideContentWithType, editPrompt: string) -> bool {
  client CustomGPT4oMini
  
  prompt #"
    Validate that the slide edit was applied correctly:
    
    **Original Slide:**
    {{ originalSlide }}
    
    **Edited Slide:**
    {{ editedSlide }}
    
    **Edit Request:**
    {{ editPrompt }}
    
    Check that:
    1. The requested changes were properly applied
    2. Element IDs and structure remain consistent
    3. Styling follows the design guidelines
    4. No elements overlap or have positioning issues
    5. Professional quality is maintained
    
    Return true if the edit was successful, false otherwise.
    Explain any issues found.
  "#
}
