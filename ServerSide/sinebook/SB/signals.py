from django.dispatch import receiver, Signal
from .tasks import get_post_suggestions, get_profile_suggestions
from .models import UserInterest

post_suggestions_signal = Signal(providing_args=["request", "instance", "user"])

@receiver(post_suggestions_signal)
def suggest_posts(sender, **kwargs):
    userid = kwargs['user'].id
    get_post_suggestions.delay(userid = userid)



profile_suggestion_signal = Signal(providing_args=["request", "user"])

def suggest_profiles(sender, **kwargs):
    userid = kwargs['user'].id
    get_profile_suggestions(userid =userid)
