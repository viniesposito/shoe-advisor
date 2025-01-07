import sys
import json
import logging
from pathlib import Path
from vector_store import ShoeKnowledgeBase
from openai import OpenAI
import os
from typing import List, Dict
from dotenv import load_dotenv
from query_cache import QueryCache

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

class ShoeAdvisor:
    def __init__(self, kb_directory: str = 'shoe_knowledge'):
        """Initialize advisor with knowledge base, OpenAI client, and cache"""
        self.client = OpenAI()  # This will use OPENAI_API_KEY from environment
        self.knowledge_base = ShoeKnowledgeBase()
        self.knowledge_base.load(kb_directory)
        self.cache = QueryCache()  # Initialize the cache
        
        self.SYSTEM_PROMPT = """You are a knowledgeable running shoe expert. 
Use the provided context to suggest similar running shoes. Your answer should contain just a few running shoes and one brief bullet point with the reasoning for the suggestion.

Format your response exactly like this example:
- **Nike Pegasus 41**
  - A solid entry-level model with good stability and comfort.
- **Nike Invincible 3**
  - Maximum cushioning and bounce for recovery runs.

Use 2-4 shoe recommendations, each with:
- Model name in bold between two newlines
- Description on a new indented line starting with a bullet point
- Keep descriptions concise (one sentence)
- Don't add any concluding text after recommendations

If you can't find enough information in the context, say so."""

    def format_context(self, chunks: List[Dict]) -> str:
        """Format chunks into context string"""
        context_parts = []
        for chunk in chunks:
            context_parts.append(f"From video '{chunk['chunk']['metadata']['title']}':")
            context_parts.append(chunk['chunk']['text'])
        return "\n\n".join(context_parts)

    def get_response(self, question: str) -> Dict:
        """Get response for user query, using cache when possible"""
        logging.debug(f"Getting response for question: {question}")
        
        try:
            # Check cache first
            cached_response = self.cache.get(question)
            if cached_response:
                logging.debug("Using cached response")
                return cached_response
            
            # If not in cache, get new response
            relevant_chunks = self.knowledge_base.search(question, k=3)
            logging.debug(f"Found {len(relevant_chunks)} relevant chunks")
            
            if not relevant_chunks:
                response = {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": []
                }
                self.cache.set(question, response)  # Cache the no-results response
                return response
            
            # Format context
            context = self.format_context(relevant_chunks)
            logging.debug("Context formatted successfully")
            
            # Create messages for GPT
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"""Context:
{context}

User Question: {question}

Please provide an answer based on the context above."""}
            ]
            
            # Get GPT response
            logging.debug("Calling OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            logging.debug("Received response from OpenAI")
            
            # Format final response with sources
            final_response = {
                "answer": answer,
                "sources": [
                    {
                        "title": chunk['chunk']['metadata']['title'],
                        "video_id": chunk['chunk']['metadata']['video_id']
                    }
                    for chunk in relevant_chunks
                ]
            }
            
            # Cache the response before returning
            self.cache.set(question, final_response)
            logging.debug("Response cached")
            
            return final_response
            
        except Exception as e:
            error_msg = f"Error in get_response: {str(e)}"
            logging.error(error_msg)
            response = {
                "error": "Failed to process request",
                "details": str(e)
            }
            # Don't cache error responses
            return response

def main():
    logging.debug("Script started")
    
    if len(sys.argv) < 2:
        error_response = {
            "error": "No question provided"
        }
        logging.error(error_response)
        print(json.dumps(error_response))
        sys.exit(1)

    try:
        question = sys.argv[1]
        logging.debug(f"Received question: {question}")
        
        # Initialize advisor
        logging.debug("Initializing ShoeAdvisor")
        advisor = ShoeAdvisor()
        
        # Get and return response
        response = advisor.get_response(question)
        logging.debug(f"Got response: {response}")
        
        # Print the JSON response
        json_response = json.dumps(response)
        print(json_response)
        
        logging.debug("Script completed successfully")
        
    except Exception as e:
        error_response = {
            "error": "Failed to process request",
            "details": str(e)
        }
        logging.error(f"Error in main: {str(e)}")
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()