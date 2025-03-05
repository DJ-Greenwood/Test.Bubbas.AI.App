# Update your chatbot/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import Conversation, Message
from .services.openai_service import OpenAIService
from ErrorLog.services.error_logger import ErrorLogger

logger = logging.getLogger(__name__)

@login_required
def chat_view(request):
    """Main chat interface view"""
    try:
        # Get user's conversations
        conversations = Conversation.objects.filter(user=request.user)
        
        # Get active conversation or create a new one
        conversation_id = request.GET.get('conversation_id')
        if conversation_id:
            try:
                conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
                # Get conversation history for existing conversation
                messages = Message.objects.filter(conversation=conversation)
            except Exception as e:
                ErrorLogger.log_error('chat', f"Error retrieving conversation {conversation_id}: {str(e)}", 
                                     request=request, user=request.user)
                # Fall back to creating a new conversation
                conversation = Conversation.objects.create(user=request.user)
                messages = []
        else:
            # Create a new conversation and save it to get an ID
            conversation = Conversation.objects.create(user=request.user)
            conversation.save()
            # For new conversations, there are no messages yet
            messages = []
        
        return render(request, 'chatbot/chat.html', {
            'conversations': conversations,
            'current_conversation': conversation,
            'messages': messages,
        })
    except Exception as e:
        ErrorLogger.log_error('chat', f"Error loading chat view: {str(e)}", request=request, user=request.user)
        messages.error(request, "There was an error loading the chat interface.")
        return redirect('home')

@login_required
@require_POST
def send_message(request):
    """API endpoint to send a message and get AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'Message cannot be empty'
            }, status=400)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
            except Exception as e:
                ErrorLogger.log_error('chat', f"Error retrieving conversation {conversation_id}: {str(e)}", 
                                     request=request, user=request.user)
                conversation = Conversation.objects.create(user=request.user)
        else:
            conversation = Conversation.objects.create(user=request.user)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Update conversation timestamp
        conversation.save()
        
        # Get conversation history (limit to last 20 messages for context)
        conversation_history = Message.objects.filter(conversation=conversation).order_by('created_at')
        
        # Limit context window to prevent token limit issues
        if conversation_history.count() > 20:
            # Always keep the first message for context
            first_message = conversation_history.first()
            # Get the most recent 19 messages (excluding the first)
            recent_messages = conversation_history.exclude(id=first_message.id).order_by('-created_at')[:19]
            # Combine the first message with the recent messages
            conversation_history = [first_message] + list(recent_messages.order_by('created_at'))
        
        # Generate AI response
        try:
            openai_service = OpenAIService()
            # Pass both conversation history and user for personalization
            ai_response = openai_service.generate_response(conversation_history, request.user)
        except Exception as e:
            error_message = f"Error generating OpenAI response: {str(e)}"
            ErrorLogger.log_error('openai', error_message, request=request, user=request.user)
            logger.error(error_message)
            ai_response = "I'm sorry, I'm having trouble connecting right now. Please try again in a moment."
        
        # Save AI response
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # Update conversation title if this is the first exchange
        if conversation_history.count() <= 2 and not conversation.title:
            # Create a title from the first user message
            title = user_message[:30] + ('...' if len(user_message) > 30 else '')
            conversation.title = title
            conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'conversation_id': conversation.id,
            'message': {
                'id': assistant_message.id,
                'content': assistant_message.content,
                'created_at': assistant_message.created_at.isoformat(),
            }
        })
    except Exception as e:
        error_message = f"Error in send_message view: {str(e)}"
        ErrorLogger.log_error('chat', error_message, request=request, user=request.user)
        logger.error(error_message)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your message.'
        }, status=500)

@login_required
def conversation_history(request, conversation_id):
    """View a specific conversation history"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages = Message.objects.filter(conversation=conversation)
        
        return JsonResponse({
            'status': 'success',
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'messages': [
                    {
                        'id': message.id,
                        'role': message.role,
                        'content': message.content,
                        'created_at': message.created_at.isoformat(),
                    }
                    for message in messages
                ]
            }
        })
    except Exception as e:
        error_message = f"Error retrieving conversation history: {str(e)}"
        ErrorLogger.log_error('chat', error_message, request=request, user=request.user)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while retrieving conversation history.'
        }, status=500)

@login_required
@require_POST
def create_conversation(request):
    """Create a new conversation"""
    try:
        conversation = Conversation.objects.create(user=request.user)
        
        return JsonResponse({
            'status': 'success',
            'conversation': {
                'id': conversation.id,
                'title': conversation.title or f"New Conversation",
                'created_at': conversation.created_at.isoformat(),
            }
        })
    except Exception as e:
        error_message = f"Error creating new conversation: {str(e)}"
        ErrorLogger.log_error('chat', error_message, request=request, user=request.user)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while creating a new conversation.'
        }, status=500)

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        conversation.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Conversation deleted successfully'
        })
    except Exception as e:
        error_message = f"Error deleting conversation {conversation_id}: {str(e)}"
        ErrorLogger.log_error('chat', error_message, request=request, user=request.user)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while deleting the conversation.'
        }, status=500)