HASHTAG_PROMPT = """You are a social media hashtag strategist.

Generate {num_hashtags} highly relevant hashtags for this video content:

Content:
{content}

Requirements:
1. Mix of popular and niche hashtags
2. Include trending hashtags if relevant
3. Target the right audience
4. Balance reach and specificity
5. Each hashtag should start with #
6. Generate exactly {num_hashtags} hashtags

Common viral hashtags to consider: #fyp #foryou #viral #trending #explore

List the hashtags one per line:
"""