from django.dispatch import receiver, Signal
from .tasks import get_page_suggestions, get_post_suggestions, get_profile_suggestions

post_suggestions_signal = Signal(providing_args=["request", "instance", "user", "suggested_posts"])

@receiver(post_suggestions_signal)
def suggest_posts(sender, **kwargs):
    userid = kwargs['user'].id
    suggested_posts = kwargs['suggested_posts']
    get_post_suggestions.delay(userid = userid, suggested_posts = suggested_posts)



profile_suggestion_signal = Signal(providing_args=["request", "user", "suggested_profiles"])

@receiver(post_suggestions_signal)
def suggest_profiles(sender, **kwargs):
    userid = kwargs['user'].id
    suggested_profiles = kwargs['suggested_profiles']
    get_profile_suggestions.delay(userid =userid, suggested_profiles=suggested_profiles)


page_suggestions_signal = Signal(providing_args=["request", "user", "suggested_pages"])

@receiver(page_suggestions_signal)
def suggest_pages(sender, **kwargs):
    userid = kwargs['user'].id
    suggested_pages = kwargs['suggested_pages']
    get_page_suggestions.delay(userid = userid, suggested_pages=suggested_pages)
