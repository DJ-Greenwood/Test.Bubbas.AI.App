from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Conversation, Message
from .services.openai_service import OpenAIService

@login_required
def chat_view(request):
    """Main chat interface view"""
    # Get user's conversations
    conversations = Conversation.objects.filter(user=request.user)
    
    # Get active conversation or create a new one
    conversation_id = request.GET.get('conversation_id')
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        # Get conversation history for existing conversation
        messages = Message.objects.filter(conversation=conversation)
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

@login_required
@require_POST
def send_message(request):
    """API endpoint to send a message and get AI response"""
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
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
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
    
    # Get conversation history
    conversation_history = Message.objects.filter(conversation=conversation)
    
    # Generate AI response
    openai_service = OpenAIService()
    ai_response = openai_service.generate_response(conversation_history)
    
    # Save AI response
    assistant_message = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=ai_response
    )
    
    return JsonResponse({
        'status': 'success',
        'conversation_id': conversation.id,
        'message': {
            'id': assistant_message.id,
            'content': assistant_message.content,
            'created_at': assistant_message.created_at.isoformat(),
        }
    })

@login_required
def conversation_history(request, conversation_id):
    """View a specific conversation history"""
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

@login_required
@require_POST
def create_conversation(request):
    """Create a new conversation"""
    conversation = Conversation.objects.create(user=request.user)
    
    return JsonResponse({
        'status': 'success',
        'conversation': {
            'id': conversation.id,
            'title': conversation.title or f"New Conversation",
            'created_at': conversation.created_at.isoformat(),
        }
    })

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Conversation deleted successfully'
    })