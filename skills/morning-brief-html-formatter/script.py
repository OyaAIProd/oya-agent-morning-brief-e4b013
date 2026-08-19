import os, json

WORD_LIMIT = 400

# (key, label, kicker-emoji, accent, deep, tint_bg, tint_border)
SECTIONS = [
    ("Artificial Intelligence", "Artificial Intelligence", "\U0001f9e0", "#6d28d9", "#4c1d95", "#faf9ff", "#ece7fb"),
    ("Technology",              "Technology",               "\u26a1", "#0369a1", "#0c4a6e", "#f7fbfe", "#e2eff8"),
    ("Business",                "Business",                 "\U0001f4c8", "#047857", "#064e3b", "#f7fdf9", "#e0f2e8"),
]

def count_words(text: str) -> int:
    return len(text.split())

def truncate_to_words(text: str, budget: int):
    words = text.split()
    used = min(len(words), budget)
    return " ".join(words[:used]) + ("\u2026" if used < len(words) else ""), used

def esc(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))

    date_string = inp.get("date_string", "").strip()
    if not date_string:
        raise ValueError("'date_string' is required (e.g. 'Monday, June 9 2025').")

    stories = inp.get("stories", [])
    if not isinstance(stories, list) or len(stories) == 0:
        raise ValueError("'stories' must be a non-empty array of story objects.")

    for i, s in enumerate(stories):
        for field in ("headline", "summary", "source_name", "url", "assigned_section"):
            if not s.get(field):
                raise ValueError(f"Story at index {i} is missing required field '{field}'.")

    # --- Identify top story ---
    top_story = next((s for s in stories if s.get("top_story")), None)

    # --- Budget tracking ---
    word_budget = WORD_LIMIT
    parts = []

    # ---- MASTHEAD (full-bleed editorial banner) ----
    parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#0b0a1f;background-image:linear-gradient(135deg,#1a1636 0%,#302b63 55%,#0b0a1f 100%);">
  <tr>
    <td style="padding:44px 40px 40px 40px;text-align:center;">
      <div style="font-family:Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:6px;color:#f5c518;text-transform:uppercase;">The Daily Edition</div>
      <div style="height:1px;background:linear-gradient(90deg,rgba(245,197,24,0) 0%,rgba(245,197,24,0.55) 50%,rgba(245,197,24,0) 100%);margin:18px auto 20px auto;width:80%;line-height:1px;font-size:0;">&nbsp;</div>
      <div style="font-family:Georgia,'Times New Roman',serif;font-size:52px;font-weight:700;color:#ffffff;letter-spacing:-1px;line-height:0.98;">Morning&nbsp;Brief</div>
      <div style="font-family:Georgia,'Times New Roman',serif;font-style:italic;font-size:15px;color:#c7d2fe;margin-top:14px;letter-spacing:0.3px;">{esc(date_string)}</div>
      <div style="height:1px;background:linear-gradient(90deg,rgba(245,197,24,0) 0%,rgba(245,197,24,0.55) 50%,rgba(245,197,24,0) 100%);margin:20px auto 0 auto;width:80%;line-height:1px;font-size:0;">&nbsp;</div>
    </td>
  </tr>
</table>
""")

    # ---- LEAD STORY (full-bleed editorial hero) ----
    if top_story:
        headline_words = count_words(top_story["headline"])
        summary_text, used = truncate_to_words(top_story["summary"], word_budget - headline_words - 5)
        word_budget -= (headline_words + used)

        parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#15131f;">
  <tr>
    <td style="padding:38px 40px 42px 40px;">
      <div style="font-family:Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:3px;color:#f5c518;text-transform:uppercase;margin-bottom:18px;">&#9733;&nbsp;&nbsp;The Lead</div>
      <div style="font-family:Georgia,'Times New Roman',serif;font-size:33px;font-weight:700;color:#ffffff;line-height:1.18;letter-spacing:-0.5px;margin-bottom:20px;">{esc(top_story["headline"])}</div>
      <table cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="width:4px;background:#f5c518;border-radius:2px;">&nbsp;</td>
          <td style="padding-left:18px;font-family:Georgia,'Times New Roman',serif;font-size:17px;font-style:italic;color:#d6d3e6;line-height:1.7;">{esc(summary_text)}</td>
        </tr>
      </table>
      <div style="margin-top:26px;">
        <a href="{esc(top_story['url'])}" style="display:inline-block;font-family:Arial,sans-serif;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#15131f;background:#f5c518;text-decoration:none;padding:13px 26px;border-radius:6px;">Read the full story &rarr;</a>
      </div>
      <div style="font-family:Arial,sans-serif;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#8b87a8;margin-top:20px;">{esc(top_story["source_name"])}</div>
    </td>
  </tr>
</table>
""")

    # ---- SECTION BLOCKS ----
    top_url = top_story["url"] if top_story else None

    for section_key, section_label, icon, accent, deep, tint_bg, tint_border in SECTIONS:
        section_stories = [
            s for s in stories
            if s.get("assigned_section") == section_key and s.get("url") != top_url
        ]
        if not section_stories:
            continue

        rows = []
        n = 0
        for s in section_stories:
            if word_budget <= 0:
                break
            h_words = count_words(s["headline"])
            summary_text, used = truncate_to_words(s["summary"], max(0, word_budget - h_words - 3))
            word_budget -= (h_words + used)
            n += 1
            num = f"{n:02d}"

            rows.append(f"""
            <tr>
              <td style="padding:0 0 4px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td valign="top" style="width:52px;font-family:Georgia,'Times New Roman',serif;font-size:30px;font-weight:700;color:{tint_border};line-height:1;padding-top:2px;">{num}</td>
                    <td valign="top" style="padding-bottom:22px;border-bottom:1px solid #ececf1;">
                      <div style="font-family:Georgia,'Times New Roman',serif;font-size:20px;font-weight:700;line-height:1.32;margin-bottom:8px;">
                        <a href="{esc(s['url'])}" style="color:#15131f;text-decoration:none;">{esc(s['headline'])}</a>
                      </div>
                      <div style="font-family:Georgia,'Times New Roman',serif;font-size:15px;color:#52525b;line-height:1.68;margin-bottom:12px;">{esc(summary_text)}</div>
                      <div style="font-family:Arial,sans-serif;font-size:11px;letter-spacing:0.5px;text-transform:uppercase;color:{accent};">
                        <span style="font-weight:700;">{esc(s['source_name'])}</span>
                        &nbsp;&nbsp;&middot;&nbsp;&nbsp;
                        <a href="{esc(s['url'])}" style="color:{accent};text-decoration:none;font-weight:700;">Read &rarr;</a>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
""")

        if not rows:
            continue

        parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;">
  <tr>
    <td style="padding:36px 40px 8px 40px;">
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="border-bottom:3px solid {accent};margin-bottom:26px;">
        <tr>
          <td style="padding-bottom:12px;">
            <span style="font-size:17px;">{icon}</span>
            <span style="font-family:Arial,sans-serif;font-size:15px;font-weight:700;letter-spacing:3px;color:{deep};text-transform:uppercase;padding-left:8px;">{esc(section_label)}</span>
          </td>
          <td align="right" style="padding-bottom:12px;font-family:Georgia,serif;font-style:italic;font-size:13px;color:#b8b8c4;">{len(rows)} {'story' if len(rows)==1 else 'stories'}</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        {"".join(rows)}
      </table>
    </td>
  </tr>
</table>
""")

    # ---- FOOTER (editorial colophon) ----
    parts.append("""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation">
  <tr>
    <td style="padding:40px 40px 44px 40px;background:#0b0a1f;background-image:linear-gradient(135deg,#1a1636 0%,#0b0a1f 100%);text-align:center;">
      <div style="font-family:Georgia,'Times New Roman',serif;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;margin-bottom:8px;">Morning Brief</div>
      <div style="height:1px;background:linear-gradient(90deg,rgba(245,197,24,0) 0%,rgba(245,197,24,0.5) 50%,rgba(245,197,24,0) 100%);margin:16px auto;width:56%;line-height:1px;font-size:0;">&nbsp;</div>
      <div style="font-family:Georgia,serif;font-style:italic;font-size:14px;color:#a9a6c4;line-height:1.6;">
        Curated tech, AI &amp; business &mdash; delivered every morning.
      </div>
    </td>
  </tr>
</table>
""")

    # ---- ASSEMBLE FULL HTML ----
    body_html = "\n".join(parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Morning Brief \u2013 {esc(date_string)}</title>
</head>
<body style="margin:0;padding:0;background:#e8e6ef;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#e8e6ef;padding:28px 0;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" role="presentation" style="max-width:640px;width:100%;background:#ffffff;border-radius:4px;overflow:hidden;box-shadow:0 10px 40px rgba(11,10,31,0.16);">
          <tr><td>{body_html}</td></tr>
        </table>
        <div style="font-family:Georgia,serif;font-style:italic;font-size:12px;color:#9aa0ac;margin-top:18px;">You&rsquo;re receiving this because you subscribed to Morning Brief.</div>
      </td>
    </tr>
  </table>
</body>
</html>"""

    subject = f"\U0001f4f0 Morning Brief \u2014 {date_string}"

    result = {
        "subject": subject,
        "html": html,
        "word_count_used": WORD_LIMIT - word_budget,
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
