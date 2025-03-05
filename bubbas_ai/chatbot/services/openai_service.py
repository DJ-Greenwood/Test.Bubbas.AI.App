from openai import OpenAI
from django.conf import settings
import logging
from .system_prompt import get_system_prompt
from ErrorLog.services.error_logger import ErrorLogger

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client =OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def _format_messages(self, conversation_history, user=None):
        """Format conversation history into OpenAI message format with enhanced system prompt"""
        formatted_messages = []
        
        # Add our enhanced system prompt
        user_name = user.username if user else None
        system_prompt = get_system_prompt(user_name)
        formatted_messages.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # Add conversation history (excluding any existing system messages)
        for message in conversation_history:
            if message.role != 'system':  # Skip old system messages
                formatted_messages.append({
                    'role': message.role,
                    'content': message.content
                })
        
        return formatted_messages
    
    def generate_response(self, conversation_history, user=None):
        """Generate a response using OpenAI API based on conversation history"""
        try:
            messages = self._format_messages(conversation_history, user)
            
            # For older OpenAI API (0.x.x)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.6,  # Encourage new topics/ideas
                frequency_penalty=0.5,  # Reduce repetition
            )
            
            # Correctly access the content based on the API response structure
            try:
                # First try the newer API format
                return response.choices[0].message.content
            except AttributeError:
                # Fall back to the older API format
                return response.choices[0].message["content"]
            
        except Exception as e:
            error_message = f"Error generating OpenAI response: {str(e)}"
            logger.error(error_message)
            
            # Log the error with more details
            error_data = {
                'model': self.model,
                'message_count': len(conversation_history) if conversation_history else 0,
                'user_id': user.id if user else None,
            }
            
            # Log error to database if we have access to the error logger
            try:
                ErrorLogger.log_error('openai', error_message, user=user, extra_data=error_data)
            except:
                # If we can't log to database, at least log to console
                logger.error(f"Additional data: {error_data}")
            
            return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."