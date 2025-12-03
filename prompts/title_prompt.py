
TITLE_PROMPT = """You are an expert at writing viral video titles for TikTok, Instagram, and YouTube Shorts.

Create a compelling title for this video (max {max_length} characters):

Content:
{content}

Requirements:
1. Capture the essence in a few words
2. Create curiosity or urgency
3. Use power words (Amazing, Shocking, Secret, Truth, etc.)
4. Make it clickable but not clickbait
5. Stay under {max_length} characters
6. NO quotes, NO hashtags

Write ONLY the title, nothing else:
"""