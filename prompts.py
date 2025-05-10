### INFORMATION TRANSFER PROMPTS ###

CATEGORY_GENERATION_PROMPT = """
Given this data entry:
Source: {source}
Content: {content}

Existing categories and their contents:
{existing_categories}

What is the most appropriate category for this information? 
You can either:
1. Choose an existing category if the content fits well with it
2. Create a new category if the content doesn't fit well with existing ones

Example category types (for new categories):
- Social Media Posts (Reddit, Twitter, etc.)
- News Articles
- Financial Reports
- Market Analysis
- Company Announcements
- Technical Analysis
- Price Predictions
- Historical Data
- Industry News

Respond with just the category name. If using an existing category, use its exact name."""
