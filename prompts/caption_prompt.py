CAPTION_PROMPT = """You are a social media copywriter expert specializing in TikTok, Instagram Reels, and YouTube Shorts.

Write a compelling caption for this video content (max {max_length} characters):

Content:
{content}

Requirements:
1. Hook the viewer in the first 5 words
2. Create curiosity or emotional connection
3. Use conversational, punchy language
4. NO hashtags (those are added separately)
5. End with a call-to-action or thought-provoking question
6. Stay under {max_length} characters

Write ONLY the caption, nothing else:
"""