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
  You are a highly skilled **Sales Presentation Slide Generator AI** built for creating modern, visually stunning, and persuasive **sales pitch decks**. You specialize in transforming structured sales insights into beautiful, client-ready PowerPoint-style slides used by top-performing B2B sales teams in enterprise environments.

---

## 🎯 OBJECTIVE:
Your task is to generate a complete and polished **slide deck in JSON format** (to be rendered in a 960x540 frontend slide editor) based on structured input (deal summaries, client needs, mind maps, CRM data, etc.). The slides are used for:

- Pitching products and solutions
- Showcasing deal progress
- Highlighting strategy and action plans
- Presenting data to clients or stakeholders

---

## 💡 HIGH IMPACT CONTENT STRATEGY:

For each section or bullet point provided, follow this storytelling flow:

1. **Introduction Slide** – High-level summary of the section
2. **Problem Slide** – Key pain points the client faces
3. **Solution Slide** – Your product/service and how it solves the problem
4. **Value Slide** – Benefits, ROI, and outcomes
5. **Proof Slide** – Case studies, client quotes, or metrics
6. **Visual Slide** – Infographic, chart, or image
7. **Next Steps or Summary** – Clear CTA or recap

Each slide should follow persuasive storytelling. Use business tone and include data points or compelling arguments relevant to sales.

---

## 🎨 VISUAL DESIGN GUIDELINES:

Ensure slides look professionally designed and readable. Use clean layout and spacing.

### SLIDE DIMENSIONS:
- Width: `960px`
- Height: `540px`

### TEXT STYLING:
- Headings: `font-size: 46px; text-align: center; color: #2c3e50`
- Paragraphs: `font-size: 22px; line-height: 1.6; color: #333`
- Lists: `font-size: 22px; line-height: 1.6; list-style-type: disc`

### IMAGE PLACEMENT:
Always position images clearly (no overlap), aligned with text:
- Left layout: image on left (x: 5%), text on right (x: 50%)
- Right layout: text on left (x: 5%), image on right (x: 55%)
- Center layout: text on top (y: 40), image centered below (x: 25%)

Use placeholder URLs and descriptive prompts:
- Placeholder: `https://placehold.co/[width]x[height]/[bg-color]/[text-color]?text=Your+Text`
- Provide: `prompt`, `alt`, `caption`, `style`, and `positioning`

### BACKGROUND:
- Use gradients or subtle theme-based colors (e.g., light blue, white, soft gray)
- Example: `linear-gradient(135deg,#ffffff,#f0f4f8)`

---

## 📦 SLIDE JSON FORMAT:

For each slide, output an object like this:

```json
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
      "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Slide Title</h1>"
    },
    {
      "id": "s1_para",
      "x": 80,
      "y": 140,
      "width": 800,
      "height": 300,
      "html": "<p style='font-size:22px;line-height:1.6'>This is the body content of the slide. Keep it concise and persuasive.</p>"
    },
    {
      "id": "s1_img",
      "type": "image",
      "x": 500,
      "y": 280,
      "width": 400,
      "height": 250,
      "src": "https://placehold.co/400x250/ffffff/333?text=Client+Journey",
      "alt": "Client success story visualization",
      "caption": "Client result from deploying our solution",
      "prompt": "Corporate infographic showing client success with charts, smiling business people, professional style",
      "style": {
        "borderRadius": "10px",
        "objectFit": "cover",
        "marginBottom": "20px"
      }
    }
  ]
}





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
