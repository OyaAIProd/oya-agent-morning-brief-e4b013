---
name: editorial-curator
display_name: "Editorial Curator"
description: "Deduplicate, score, and select the top 5–7 news stories across Technology, AI, and Business for newsletter publication."
category: productivity
icon: newspaper
skill_type: sandbox
catalog_type: addon
tool_schema:
  name: editorial_curator
  description: "Deduplicate and editorially rank raw article objects, returning the top 5–7 stories with headlines, summaries, and section assignments, plus a skip_send flag."
  parameters:
    type: object
    properties:
      articles:
        type: array
        description: "List of raw article objects to curate."
        items:
          type: object
          properties:
            title:
              type: string
              description: "Original article title."
            url:
              type: string
              description: "Article URL."
            source:
              type: string
              description: "Publisher or source name."
            body_excerpt:
              type: string
              description: "Short excerpt or summary of the article body."
            topic:
              type: string
              description: "Broad topic tag, e.g. 'AI', 'Technology', 'Business'."
          required: [title, url, source, body_excerpt, topic]
    required: [articles]
---
# Editorial Curator
Deduplicate, score, and select the top 5–7 news stories across Technology, AI, and Business topics for newsletter publication.

## Be Proactive
Call this skill whenever a list of raw articles has been gathered and needs to be filtered and ranked before sending a newsletter or briefing. Invoke it automatically after any news-fetch step.