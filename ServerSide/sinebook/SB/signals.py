from django.dispatch import receiver, Signal
from .tasks import get_page_suggestions, get_post_suggestions, get_profile_suggestions

post_suggestions_signal = Signal(providing_args=["request", "instance", "user"])

@receiver(post_suggestions_signal)
def suggest_posts(sender, **kwargs):
    userid = kwargs['user'].id
    get_post_suggestions.delay(userid = userid)



profile_suggestion_signal = Signal(providing_args=["request", "user"])

@receiver(post_suggestions_signal)
def suggest_profiles(sender, **kwargs):
    userid = kwargs['user'].id
    get_profile_suggestions.delay(userid =userid)


page_suggestions_signal = Signal(providing_args=["request", "user"])

@receiver(page_suggestions_signal)
def suggest_pages(sender, **kwargs):
    userid = kwargs['user'].id
    get_page_suggestions.delay(userid = userid)
