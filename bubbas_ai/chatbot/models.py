from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title or f"Conversation {self.id}"
    
    def save(self, *args, **kwargs):
        # First save the object to ensure it has a primary key
        super().save(*args, **kwargs)
        
        # Then try to generate a title from the first message if no title exists
        if not self.title:
            try:
                first_message = self.messages.first()
                if first_message:
                    # Limit title to first 30 characters of the message
                    self.title = first_message.content[:30] + ('...' if len(first_message.content) > 30 else '')
                    # Save again with the new title
                    super().save(update_fields=['title'], *args, **kwargs)
            except:
                # If there's an error (like when the relationship can't be used yet), just continue
                pass

class Message(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"