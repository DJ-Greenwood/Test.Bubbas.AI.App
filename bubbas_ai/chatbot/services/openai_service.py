from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        logger.debug("Initializing OpenAIService")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        logger.debug(f"OpenAI client initialized with model: {self.model}")
        print(f"OpenAI client initialized with model: {self.model}")
    
    def _format_messages(self, conversation_history):
        """Format conversation history into OpenAI message format"""
        logger.debug("Formatting conversation history into OpenAI message format")
        formatted_messages = []
        
        # Add system message if it doesn't exist
        if not any(msg.role == 'system' for msg in conversation_history):
            logger.debug("Adding system message to formatted messages")
            print("Adding system message to formatted messages")

            formatted_messages.append({
                'role': 'system',
                'content': 'You are Bubbas, a helpful AI assistant created by Bubbas.ai.'
            })
        
        # Add conversation history
        for message in conversation_history:
            formatted_messages.append({
                'role': message.role,
                'content': message.content
            })
        
        logger.debug(f"Formatted messages: {formatted_messages}")
        print(f"Formatted messages: {formatted_messages}")

        return formatted_messages
    
    def generate_response(self, conversation_history):
        """Generate a response using OpenAI API based on conversation history"""
        try:
            logger.info(f"Generating OpenAI response for conversation history: {conversation_history}")
            print(f"Generating OpenAI response for conversation history: {conversation_history}")

            messages = self._format_messages(conversation_history)
            logger.debug(f"Formatted messages for OpenAI API: {messages}")
            print(f"Formatted messages for OpenAI API: {messages}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            logger.info("OpenAI response generated successfully")
            print("OpenAI response generated successfully")

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            print(f"Error generating OpenAI response: {str(e)}")

            return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."