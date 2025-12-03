VIRALITY_PROMPT = """You are an expert social media analyst specializing in viral content on TikTok, Instagram Reels, and YouTube Shorts.

Analyze the following video content and score it on these dimensions (0-100 for each):

Content:
{content}

Provide scores for:
1. **Virality** (0-100): Potential to go viral based on:
   - Hook strength in first 3 seconds
   - Emotional impact
   - Shareability
   - Trend alignment
   - Controversy or uniqueness

2. **Emotion** (0-100): Emotional intensity:
   - How strongly does it evoke emotion?
   - Is there surprise, humor, inspiration, or shock?
   - Does it make you FEEL something?

3. **Hook** (0-100): First impression quality:
   - Does it grab attention immediately?
   - Would someone stop scrolling?
   - Is there a compelling opening statement?

4. **Completeness** (0-100): Storytelling quality:
   - Does it tell a complete mini-story?
   - Is there a beginning, middle, and end?
   - Does it have a payoff or conclusion?

Respond ONLY with a JSON object in this exact format:
{{
  "virality": 85,
  "emotion": 90,
  "hook": 75,
  "completeness": 80
}}

Be honest and critical. Most content should score between 30-70. Only truly exceptional content should score above 85.
"""