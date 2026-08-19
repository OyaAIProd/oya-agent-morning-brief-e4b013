---
name: morning-brief-html-formatter
display_name: "Morning Brief HTML Formatter"
description: "Transforms editorial story objects into a fully inline-styled HTML email string and subject line for Morning Brief newsletters."
category: productivity
icon: newspaper
skill_type: sandbox
catalog_type: addon
tool_schema:
  name: morning_brief_html_formatter
  description: "Build a single inline-styled HTML email string (plus plain-text subject) from a date string and an array of editorial story objects."
  parameters:
    type: object
    properties:
      date_string:
        type: "string"
        description: "Human-readable date for the newsletter header, e.g. 'Monday, June 9 2025'."
      stories:
        type: "array"
        description: "Array of story objects from the editorial skill. Each object must have: headline (string), summary (string), source_name (string), url (string), assigned_section (string: 'Artificial Intelligence' | 'Technology' | 'Business'), top_story (boolean)."
        items:
          type: "object"
    required: [date_string, stories]
---
# Morning Brief HTML Formatter
Converts a date and an array of editorial story objects into a production-ready inline-styled HTML email and subject line.

## Be Proactive
Call this immediately after the editorial skill returns its story objects whenever the user wants to produce, preview, or send a Morning Brief newsletter email.