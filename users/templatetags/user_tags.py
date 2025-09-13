from django import template
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter
def is_admin(user):
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', None) == 'admin')