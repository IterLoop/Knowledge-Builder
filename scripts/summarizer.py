 
# scripts/summarizer.py
# Summarizes text using OpenAI GPT-4.

import logging
from typing import List, Optional
import openai

from scripts.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Set the OpenAI API key from config
openai.api_key = OPENAI_API_KEY

def summarize_text(texts: List[str]) -> Optional[str]:
    """
    Summarize a list of text strings using OpenAI's GPT-4.

    :param texts: List of text contents to summarize.
    :return: A summary string or None on failure.
    """
    try:
        combined_text = " ".join(texts)
        logger.info("Sending text to GPT-4 for summarization...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant summarizing content."},
                {"role": "user", "content": combined_text}
            ]
        )
        summary = response["choices"][0]["message"]["content"]
        logger.info("Received summary from GPT-4., ")
        return summary
    except Exception as e:
        logger.error(f"Failed to summarize: {e}")
        return None
