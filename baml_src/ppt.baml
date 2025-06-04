// PowerPoint presentation generation schema

// Input structures
class OutlinePoint {
  text string @description("The text content of the bullet point")
}

class OutlineSection {
  id int @description("Unique identifier for the section")
  title string @description("The title of the section")
  points string[] @description("List of bullet points for this section")
}

class PresentationInput {
  id int @description("Unique identifier for the presentation")
  title string @description("The title of the presentation")
  outline OutlineSection[] @description("The sections that make up the presentation outline")
}

// Output structures for slide elements and styling
class ImageElement {
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
  style ImageStyle @description("Style properties for the image")
}

class ImageStyle {
  borderRadius string @description("Border radius of the image, e.g. '8px'")
  objectFit string @description("How the image should fit its container, e.g. 'cover'")
  marginBottom string @description("Margin below the image block, e.g. '20px'")
}

class SlideElement {
  id string @description("Unique identifier for the element, e.g. s1_title, s1_para")
  x int @description("X position of the element in pixels from left")
  y int @description("Y position of the element in pixels from top") 
  width int @description("Width of the element in pixels")
  height int @description("Height of the element in pixels")
  html string @description("HTML content with required styling. Example: <h1 style='text-align:center;font-size:46px;color:#2c3e50'>Title Text</h1>")
}

class SlideContent {
  slide_id string @description("Unique identifier for the slide, e.g. slide_1")
  background string @description("Background style or color of the slide. Example: linear-gradient(135deg,#ffffff,#f0f4f8)")
  content (SlideElement | ImageElement)[] @description("List of elements on the slide")
}

// The function that generates a PowerPoint presentation
function GeneratePresentation(input: PresentationInput) -> SlideContent[] {
  client Gemini20Flash
  
  prompt #"
    You are a professional **Slide Generation AI Assistant** built for modern sales teams. Your role is to help salespeople generate **polished, client-facing PowerPoint slides** from structured sales data — including deal summaries, mind maps, client notes, and strategy outlines.

    ---

    ## 🎯 PURPOSE:

    This tool helps **sales professionals** save time and effort by instantly turning structured sales input (like mind maps or outlines) into **comprehensive, ready-to-present slides**. These slides are typically used to:

    - Pitch products or solutions to clients
    - Summarize key deal conversations
    - Share strategies or action plans
    - Present progress and updates to stakeholders

    The final slide deck should be professional, visually engaging, content-rich, and tailored for **external presentation to clients or decision-makers**.

    ---

    ## 📥 DATA SOURCE:

    The structured input you'll receive is derived from:
    - AI-generated **Deal Summaries**
    - Sales meeting transcripts
    - Salesperson-entered mind maps and outlines
    - CRM-extracted insights and notes

    This information has already been pre‑processed into a structured mind map format that you will use to build the slides.

    ---

    ## 🧠 YOUR ROLE:

    As the assistant, your job is to:
    1. **Content Expansion Strategy:**
       - For EACH bullet point, create a minimum of 2-3 detailed slides
       - Break down complex topics into step-by-step explanations
       - Add industry statistics, market data, and trend analysis
       - Include real-world case studies and success stories
       - Provide expert quotes and industry leader insights
       - Add competitor analysis and market positioning
    
    2. **Mandatory Slide Generation Requirements:**
       - Generate MINIMUM 7-9 slides for EACH major section
       - Create 2-3 detail slides for EACH bullet point provided
       - Include transition slides between sections
       - Add comprehensive summary slides after each section
    
    3. **Required Slide Types for Each Section:**
       a. Introduction Slides:
          - Section title and overview
          - Key statistics and market data
          - Current challenges and opportunities
          - Context and background information
       
       b. Detailed Content Slides:
          - In-depth analysis for each point
          - Supporting data and evidence
          - Case studies and examples
          - Implementation strategies
          - Best practices and recommendations
       
       c. Supporting Slides:
          - Visual representations (charts, graphs, infographics)
          - Comparison tables and matrices
          - Timeline and roadmap slides
          - Risk analysis and mitigation strategies
    
    4. **Content Enhancement Rules:**
       - Every major point must be expanded with:
         * Background context and market analysis
         * Detailed technical explanation
         * Supporting data and statistics
         * Real-world examples and case studies
         * Implementation guidelines
         * Success metrics and KPIs
         * Future trends and predictions
       - Include expert opinions and research findings
       - Add competitive landscape analysis
       - Provide actionable recommendations
    
    5. **Professional Polish Requirements:**
       - Use modern design best practices
       - Ensure consistent visual hierarchy
       - Include executive-level summaries
       - Add detailed footnotes and references
       - Maintain professional branding throughout
       - Use high-quality visuals and professional icons

    ---

    ## 🎨 Theme Behavior:

    - If mindMapJson.theme is "light":
      - Use **varied light backgrounds** (e.g., white, off-white, subtle light gradients, very light blues or grays as specified in Design Guidelines).
      - Use **dark text colors** with adequate contrast (e.g., deep blues, charcoal, rich browns, dark navy) for headings and paragraphs.
      - Use accent colors like soft blues (#4285F4), subtle greens (#34A853), light teals (#00ACC1), or gentle oranges (#FB8C00).
    - If mindMapJson.theme is "dark":
      - Use **varied dark backgrounds** (e.g., deep blue-blacks, rich charcoals, subtle dark gradients as specified in Design Guidelines).
      - Use **light text colors** with excellent contrast (e.g., off-whites, soft creams, light grays) for headings and paragraphs.
      - Use accent colors like vibrant teals (#00BCD4), glowing purples (#AB47BC), bright cyans (#00E5FF), or warm ambers (#FFD740).

    The design should always be visually coherent, modern, and extremely easy to read, following the **DESIGN & STYLE GUIDELINES**.

    ---

    ## 🌟 DESIGN & STYLE GUIDELINES:

    Your generated slides must be visually stunning, contemporary, and executive-level professional. Adhere to these principles:


    TEXT ELEMENT STYLES:
    - Headings: style='text-align:center;font-size:46px;color:#2c3e50'
    - Paragraphs: style='font-size:22px;line-height:1.55'
    - Lists: style='font-size:22px;line-height:1.6;list-style-type:disc'

    IMAGE GUIDELINES:
    1. Position images strategically:
       - Right-side: x=55% of slide width, width=40% (with text at x=5%)
       - Left-side: x=5%, width=40% (with text at x=50%)
       - Center below text: x=25%, width=50%
    2. Include for each image:
       - Detailed prompt describing the desired visual
       - Placeholder URL (https://placehold.co/[width]x[height]/[bg-color]/[text-color])
       - Alt text and caption
       - Style properties (borderRadius, objectFit, marginBottom)
    3. Ensure no overlap between images and text
    4. Match image theme colors with slide background

    Example slide structure:
    {
      "slide_id": "slide_1",
      "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
      "content": [
        {
          "id": "s1_title",
          "x": 120,
          "y": 40,
          "width": 960,
          "height": 60,
          "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Title Text</h1>"
        },
        {
          "id": "s1_img",
          "type": "image",
          "x": 250,
          "y": 300,
          "width": 600,
          "height": 250,
          "src": "https://placehold.co/600x400/ffffff/222?text=AI+Healthcare",
          "alt": "AI-powered medical analysis visualization",
          "caption": "Next-generation healthcare diagnostics",
          "prompt": "3D visualization of AI analyzing medical scans, with floating holographic medical data and neural network connections in a modern medical setting. Style: Clean, professional, blue and white color scheme.",
          "style": {
            "borderRadius": "8px",
            "objectFit": "cover",
            "marginBottom": "20px"
          }
        }
      ]
    }

    SLIDE CONTENT REQUIREMENTS:
    1. Element IDs must follow pattern: s1_title, s1_para, etc.
    2. Coordinates (x,y) determine position from top-left
    3. Width and height must be appropriate for content
    4. All HTML must include inline styles
    5. Use consistent styling across similar elements

    The presentation outline is:
    {{ ctx.output_format }}
  "#
}

// Test function for validating slide generation
test PresentationGenerationTest {
  functions [GeneratePresentation]
  args {
    input {
      id 12345
      title "Sample Presentation"
      outline [
        {
          id 1
          title "Introduction"
          points [
            "Key point 1",
            "Key point 2",
            "Key point 3"
          ]
        }
      ]
    }
  }
}


test PresentationGenerationTese {
  functions [GeneratePresentation]
  args {
    input {
      id 12346
      title "AI in Healthcare: Transforming the Future of Medicine"
      outline [
        {
          id 1
          title "Introduction: The AI Revolution in Healthcare"
          points [
            "The rising tide of AI in healthcare: Improved patient care, diagnostics, and clinical efficiency.",
            "Visual: Modern hospital overlaid with circuit-style AI iconography.",
            "Presenter details and organization.",
            "Thesis statement: AI is poised to revolutionize healthcare, offering unprecedented opportunities for improved patient outcomes and operational efficiency."
          ]
        },
        {
          id 2
          title "Evolution of AI in Healthcare: From Concept to Reality"
          points [
            "Early applications: Expert systems and rule-based AI.",
            "The rise of machine learning: Algorithms learning from data to improve accuracy and efficiency.",
            "Deep learning's impact:  Advanced image analysis, natural language processing.",
            "Current landscape: A blend of established and emerging AI technologies."
          ]
        },
        {
          id 3
          title "Real-World Applications: AI in Action"
          points [
            "Improved Diagnostics: AI-powered image analysis for faster and more accurate diagnosis of diseases (e.g., cancer detection).",
            "Personalized Medicine: Tailoring treatments based on individual patient data and genetic information.",
            "Drug Discovery and Development: Accelerating the process of identifying and developing new drugs.",
            "Robotic Surgery: Enhancing precision and minimizing invasiveness in surgical procedures."
          ]
        },
        {
          id 4
          title "Innovative AI Solutions: Shaping the Future"
          points [
            "AI-powered virtual assistants for patient support and engagement.",
            "Predictive analytics for hospital resource allocation and patient risk stratification.",
            "Wearable sensors and remote patient monitoring: Continuous health data collection and early warning systems.",
            "Blockchain technology for secure and transparent data management."
          ]
        },
        {
          id 5
          title "Ethical Considerations and Challenges"
          points [
            "Data privacy and security: Protecting sensitive patient information.",
            "Algorithmic bias: Ensuring fairness and equity in AI-driven healthcare decisions.",
            "Regulatory frameworks: Navigating the complex landscape of AI regulations.",
            "Transparency and explainability: Understanding how AI systems arrive at their conclusions."
          ]
        },
        {
          id 6
          title "Overcoming Challenges: Fostering Collaboration and Innovation"
          points [
            "Collaboration between AI experts, healthcare professionals, and policymakers.",
            "Investing in research and development to improve AI algorithms and applications.",
            "Addressing workforce needs: Training and upskilling healthcare professionals in AI.",
            "Establishing clear ethical guidelines and standards for AI in healthcare."
          ]
        },
        {
          id 7
          title "The Next 5-10 Years: A Vision for AI-Powered Healthcare"
          points [
            "Increased integration of AI across all aspects of healthcare delivery.",
            "More personalized and proactive care based on predictive analytics and remote monitoring.",
            "Significant improvements in diagnostic accuracy and treatment efficacy.",
            "Wider accessibility and affordability of AI-driven healthcare solutions."
          ]
        },
        {
          id 8
          title "Case Study 1: Successful AI Implementation in [Specific Hospital/Organization]"
          points [
            "Detailed description of the AI solution implemented.",
            "Quantifiable results and positive impact on patient care and operational efficiency.",
            "Lessons learned and best practices for successful AI adoption.",
            "Visual: Charts and graphs showcasing key performance indicators (KPIs)."
          ]
        }
        {
          id 12
          title "Q&A Session: Engaging with the Audience"
          points [
              "Open the floor for questions from the audience.",
              "Be prepared to answer questions about your company, technology, market, and financial projections.",
              "Engage with the audience and address any concerns or doubts they may have."
          ]
        }
      ]
    }
  }
}


// Function to validate presentation structure
function ValidatePresentation(slides: SlideContent[]) -> bool {
  client CustomGPT4oMini
  
  prompt #"
    Validate that the presentation structure meets these requirements:
    1. Each slide has a unique slideId following pattern slide_[number]
    2. Each element has:
       - Unique elementId following pattern s[number]_[type]
       - Valid x,y coordinates and dimensions
       - HTML with proper inline styles following these patterns:
         * Headings: style='text-align:center;font-size:46px;color:#2c3e50'
         * Paragraphs: style='font-size:22px;line-height:1.55'
         * Lists: style='font-size:22px;line-height:1.6;list-style-type:disc'
    3. Background values are valid CSS (hex, rgb, rgba, or gradient)
    4. Text styling is consistent across similar elements
    
    Slides to validate:
    {{ slides }}

    Return true if valid, false if any issues are found.
    Explain any validation failures.
  "#
}
