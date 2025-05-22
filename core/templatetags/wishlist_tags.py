from django import template
from core.models import Wishlist  # Adjust if your Wishlist model is in a different app

register = template.Library()

@register.filter(name='wishlist_item_count')
def wishlist_item_count(user):
    if user.is_authenticated:
        return Wishlist.objects.filter(user=user).count()  # Count wishlist items for the authenticated user
    return 0
