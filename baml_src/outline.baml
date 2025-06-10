// Strategic Sales Presentation Outline Generator

// Input structures for dynamic context
class DynamicInputContext {
  content string @description("User's primary request/prompt")
  audience_type string? @description("Target audience type, e.g. 'Executive Leadership', 'Technical Buyers', 'C-Suite'")
  scenario string? @description("Presentation scenario, e.g. 'First-time pitch to new potential client'")
  tone string? @description("Desired tone, e.g. 'Formal and data-driven', 'Confident and inspiring'")
  pages string? @description("Presentation length, e.g. '10-12 slides'")
  meeting_deal_summary string? @description("JSON-formatted summary of previous meeting transcript containing customer insights, pain points, stakeholders, and deal details")
  file_context string? @description("Relevant text extracted from attached files")
}

// Analysis and synthesis structures
class CustomerAnalysis {
  core_problem string @description("Central business problem as a gap between current and desired state")
  business_consequences string @description("Quantified cost or risk of not solving this problem")
  ideal_customer_profile string @description("Description of the company being pitched to")
  key_stakeholders string[] @description("List of stakeholders and their motivations")
  anticipated_objections string[] @description("Most likely fears or pushbacks with counter-arguments")
}

class MarketPosition {
  market_context string @description("Key trend making this problem urgent right now")
  unique_value_proposition string @description("Unique positioning as 'Only we...' statement")
  data_proof string[] @description("Relevant facts, metrics that build trust")
  social_proof string[] @description("Client testimonials, case studies")
  technical_proof string[] @description("Technical capabilities, integrations")
}

class StrategicSalesPlan {
  presenter_role string @description("Role of the person presenting")
  presentation_task string @description("Specific goal of this presentation")
  primary_cta string @description("Single, clear, low-friction action for audience")
  customer_analysis CustomerAnalysis @description("Deep dive into customer context")
  market_position MarketPosition @description("Market landscape and positioning")
}

// Presentation outline structures
class SlideDetail {
  id int @description("Unique identifier for the slide")
  title string @description("Customer-centric and impactful slide title")
  objective string @description("Strategic purpose of this slide in the narrative")
  key_content_elements string[] @description("Essential points, data, or claims for the slide")
  visual_concept string @description("Suggestion for slide's visual design")
  sales_narrative string @description("Detailed, persuasive script addressing stakeholder motivations")
  strategic_justification string @description("Intended psychological impact on audience")
}

class StrategicPresentationOutline {
  title string @description("Overall presentation title")
  id int @description("Unique identifier for the presentation")
  strategic_plan StrategicSalesPlan @description("The synthesized strategic sales plan")
  slides SlideDetail[] @description("Detailed slide-by-slide outline following Problem->Promised Land->Bridge->Proof->Plan narrative")
}

// Main function for strategic analysis and outline generation
function GenerateStrategicSalesOutline(input: DynamicInputContext) -> StrategicPresentationOutline {
  client Gemini20Flash
  prompt #"
    You are an elite sales strategist and presentation expert. Your task is to create a comprehensive strategic sales presentation outline from the provided inputs.

    PART 1: DYNAMIC INPUT CONTEXT
    User's Core Request: {{ input.content }}
    {% if input.audience_type %}Audience Type: {{ input.audience_type }}{% endif %}
    {% if input.scenario %}Scenario: {{ input.scenario }}{% endif %}
    {% if input.tone %}Desired Tone: {{ input.tone }}{% endif %}
    {% if input.pages %}Presentation Length: {{ input.pages }}{% endif %}
    {% if input.meeting_deal_summary %}Meeting Deal Summary: {{ input.meeting_deal_summary }}{% endif %}
    {% if input.file_context %}File Context: {{ input.file_context }}{% endif %}

    PART 2: ANALYSIS & SYNTHESIS ENGINE
    Before generating the outline, perform a deep analysis and create a strategic sales plan.

    {% if input.meeting_deal_summary %}
    MEETING DEAL SUMMARY ANALYSIS:
    The following is a JSON-formatted meeting summary. Extract key strategic insights:
    {{ input.meeting_deal_summary }}
    
    Focus specifically on:
    - Customer pain points and challenges discussed
    - Product/service benefits that resonated with attendees
    - Pricing and budget considerations mentioned
    - Stakeholders involved and their roles/motivations
    - Objections raised and how they were addressed
    - Decision-making timeline and process insights
    - Competitive landscape mentioned
    - Next steps and follow-up actions identified
    - Buying signals or indicators of interest
    {% endif %}

    {% if input.file_context %}
    FILE CONTEXT ANALYSIS:
    Extract supporting evidence from the provided context:
    {{ input.file_context }}
    
    Focus on:
    - Key statistics, data points, and metrics
    - Quotes and testimonials that add credibility
    - Value propositions and unique selling points
    - Technical specifications or capabilities
    - Success stories and case studies
    - Market research or competitive intelligence
    {% endif %}

    PART 3: PRESENTATION GENERATION
    You must respond with a valid JSON object in the following format. Do not include any other text, markdown, or explanations:

    {
      "title": "Overall Presentation Title",
      "id": 12345,
      "strategic_plan": {
        "presenter_role": "Role of the person presenting (e.g., Sales Lead, Solutions Architect)",
        "presentation_task": "Specific goal of this presentation",
        "primary_cta": "Single, clear, low-friction action for audience",
        "customer_analysis": {
          "core_problem": "Central business problem as a gap between current and desired state",
          "business_consequences": "Quantified cost or risk of not solving this problem",
          "ideal_customer_profile": "Description of the company being pitched to",
          "key_stakeholders": ["List of stakeholders and their motivations"],
          "anticipated_objections": ["Most likely fears or pushbacks with counter-arguments"]
        },
        "market_position": {
          "market_context": "Key trend making this problem urgent right now",
          "unique_value_proposition": "Unique positioning as 'Only we...' statement",
          "data_proof": ["Relevant facts, metrics that build trust"],
          "social_proof": ["Client testimonials, case studies"],
          "technical_proof": ["Technical capabilities, integrations"]
        }
      },
      "slides": [
        {
          "id": 1,
          "title": "Customer-centric, impactful slide title",
          "objective": "Strategic purpose of this slide in the narrative",
          "key_content_elements": ["Essential points", "Data or claims", "For the slide"],
          "visual_concept": "Suggestion for slide's visual design",
          "sales_narrative": "Detailed, persuasive script addressing stakeholder motivations",
          "strategic_justification": "Intended psychological impact on audience"
        }
      ]
    }

    Create a detailed slide-by-slide outline that follows the persuasive sales narrative arc:
    Problem -> Promised Land -> Bridge -> Proof -> Plan

    The presentation should be compelling, data-driven, and tailored to the specific audience and scenario provided.
  "#
}

// Simplified function for quick outline generation (backward compatibility)
function GenerateQuickOutline(
  content: string,
  audience: string?,
  pages: string?,
  scenario: string?,
  tone: string?
) -> StrategicPresentationOutline {
  client Gemini20Flash
  prompt #"
    Based on the following content, generate a detailed strategic presentation outline:

    Content: {{ content }}
    {% if audience %}Audience: {{ audience }}{% endif %}
    {% if pages %}Pages: {{ pages }}{% endif %}
    {% if scenario %}Scenario: {{ scenario }}{% endif %}
    {% if tone %}Tone: {{ tone }}{% endif %}

    Create a presentation outline that includes:
    1. Strategic analysis of the audience and context
    2. Clear value proposition and positioning
    3. Detailed slide-by-slide breakdown
    4. Sales narrative for each slide
    5. Visual concepts and content elements

    Follow the Problem -> Promised Land -> Bridge -> Proof -> Plan narrative structure.
    Make each slide customer-centric and action-oriented.
  "#
}
    

