from celery import shared_task

from .models import FieldPages, HashTag, PagePostList, UserInterest, Page, SBUser, Post, Tags
from datetime import datetime, timedelta
from django.utils import timezone

def post_suggestions(userid):
    i = 10
    requesting_userid = userid
    requesting_sb_user = SBUser.objects.prefetch_related(
        'friends').get(user_id=requesting_userid)
    user_interest = UserInterest.objects.prefetch_related(
        'suggested_posts', 'followed_pages', 'likes').get(user_id=requesting_userid)
    recently_suggested_posts = user_interest.suggested_posts.all()
    user_posts_to_be_suggested = Post.objects.none()
    friends_list = requesting_sb_user.friends.all()
    #delete record of posts which has been suggested two days ago to the user.
    user_interest.suggested_posts.through.objects.filter(suggested_at__lt = timezone.now()-timedelta(days=2)).delete()
    #Above line ensures the deletion of useless data.
    '''
    Posts by the friends, posted within 2 days, are being listed and ordered with respect to score
    as well as recently suggested posts are being excluded.
    '''
    if len(friends_list) > 0:
        for friend in friends_list:
            friend_interest = UserInterest.objects.prefetch_related(
                'posts').get(user_id=friend.user_id)
            friends_recent_posts = friend_interest.posts.filter(
                posted_at__gte=timezone.now() - timedelta(days=2)).exclude(who_can_see='None')
            user_posts_to_be_suggested = user_posts_to_be_suggested.union(
                friends_recent_posts)
    user_posts_to_be_suggested = user_posts_to_be_suggested.difference(
        recently_suggested_posts)
    ordered_posts_by_user_to_be_suggested = user_posts_to_be_suggested.order_by(
        '-score')
    number_of_suggested_posts_by_user = len(user_posts_to_be_suggested)
    if number_of_suggested_posts_by_user >= i:
        suggested_posts = ordered_posts_by_user_to_be_suggested[0:i]
        user_interest.posts_to_be_suggested.set(list(suggested_posts))
        user_interest.suggested_at = datetime.now()
        user_interest.save()
        return suggested_posts
        # level 1 of posts by user for suggestions is completed.
    else:
        '''
        Posts By the pages followed by the user, posted within last 2 days are being listed for suggestions.
        '''
        required_number_of_posts = i - number_of_suggested_posts_by_user
        page_posts_to_be_suggested = Post.objects.none()
        if len(user_interest.followed_pages.all()) > 0:
            for page in user_interest.followed_pages.all():
                post_page_instance = PagePostList.objects.prefetch_related(
                    'posts').get(page_id=page.id)
                page_recent_posts = post_page_instance.posts.filter(
                    posted_at__gte=timezone.now() - timedelta(days=2))
                page_posts_to_be_suggested = page_posts_to_be_suggested.union(
                    page_recent_posts)
        page_posts_to_be_suggested = page_posts_to_be_suggested.difference(
            recently_suggested_posts)
        ordered_posts_by_page_to_be_suggested = page_posts_to_be_suggested.order_by(
            '-score')
        number_of_page_posts_to_be_suggested = len(
            page_posts_to_be_suggested)
        if number_of_page_posts_to_be_suggested >= required_number_of_posts:
            required_page_posts = ordered_posts_by_page_to_be_suggested[
                0:required_number_of_posts]
            suggested_posts = user_posts_to_be_suggested.union(
                required_page_posts)
            user_interest.posts_to_be_suggested.set(list(suggested_posts))
            user_interest.suggested_at = datetime.now()
            user_interest.save()
            return suggested_posts
            # level 1 of posts by page, for suggestions, is completed.
        else:
            '''
            Posts by the pages, whose posts has been liked recently, posted within 2 days are listed.
            '''
            required_number_of_posts = i - \
                (number_of_suggested_posts_by_user +
                    number_of_page_posts_to_be_suggested)
            page_post_likes = user_interest.likes.exclude(
                post__page__isnull=True).order_by('-liked_at')
            unknown_page_posts_to_be_suggested = Post.objects.none()
            if len(page_post_likes) > 0:
                if len(page_post_likes) > 20:
                    page_post_likes = page_post_likes[0: 20]
                for like in page_post_likes:
                    posting_page_id = like.post.page_id
                    if user_interest.followed_pages.filter(id=posting_page_id).exists() == False:
                        post_page_list_instance = PagePostList.objects.prefetch_related(
                            'posts').get(page_id=posting_page_id)
                        posts_list_by_page = post_page_list_instance.posts.filter(
                            posted_at__gte=timezone.now() - timedelta(days=2))
                        unknown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.union(
                            posts_list_by_page)
            unknown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.difference(
                recently_suggested_posts, page_posts_to_be_suggested)
            ordered_unkown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.order_by(
                '-score')
            if len(unknown_page_posts_to_be_suggested) >= required_number_of_posts:
                required_page_posts = ordered_unkown_page_posts_to_be_suggested[
                    0:required_number_of_posts]
                suggested_posts = user_posts_to_be_suggested.union(
                    page_posts_to_be_suggested, required_page_posts)
                user_interest.posts_to_be_suggested.set(list(suggested_posts))
                user_interest.suggested_at = datetime.now()
                user_interest.save()
                return suggested_posts
                # level 2 of posts by page, to be suggested, has completed.
            else:
                '''
                Posts by user, whose recent posts has been liked by the requesting user recently, posted within last 2 days, are listed.
                '''
                required_number_of_posts = i - \
                    (number_of_suggested_posts_by_user +
                        number_of_page_posts_to_be_suggested)
                user_post_likes = user_interest.likes.filter(
                    post__page__isnull=True).order_by('-liked_at')
                unknown_user_posts_to_be_suggested = Post.objects.none()
                if len(user_post_likes) > 0:
                    if len(user_post_likes) > 20:
                        user_post_likes = user_post_likes[0:20]
                    for like in user_post_likes:
                        posting_user_id = like.post.user_id
                        if requesting_sb_user.friends.filter(user_id=posting_user_id).exists() == False:
                            liked_user_interest_instance = UserInterest.objects.prefetch_related(
                                'posts').get(user_id=posting_user_id)
                            posts_list_by_user = liked_user_interest_instance.posts.filter(
                                posted_at__gte=timezone.now() - timedelta(days=2)).filter(who_can_see='Public')
                            unknown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.union(
                                posts_list_by_user)
                unknown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.difference(
                    recently_suggested_posts, user_posts_to_be_suggested)
                ordered_unkown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.order_by(
                    '-score')
                if len(unknown_user_posts_to_be_suggested) >= required_number_of_posts:
                    required_user_posts = ordered_unkown_user_posts_to_be_suggested[
                        0:required_number_of_posts]
                    suggested_posts = user_posts_to_be_suggested.union(required_user_posts, unknown_page_posts_to_be_suggested,
                                                                        page_posts_to_be_suggested)
                    user_interest.posts_to_be_suggested.set(list(suggested_posts))
                    user_interest.suggested_at = datetime.now()
                    user_interest.save()
                    return suggested_posts
                    # level 2 of posts by user, to be suggested, has completed.

                else:
                    '''
                    Posts by those pages which have same hashtags as in recently 10 liked posts, calculated based on top 3 most used tags, by the user have, are being listed.
                    '''
                    required_number_of_posts = required_number_of_posts - \
                        len(unknown_user_posts_to_be_suggested)
                    tags_of_reacted_page_posts = Tags.objects.none()
                    tagged_page_posts_to_be_suggested = Post.objects.none()
                    most_liked_tags_id_list = []
                    if len(page_post_likes) > 0:
                        if len(page_post_likes) > 10:
                            page_post_likes = page_post_likes[0:10]
                        for like in page_post_likes:
                            if len(like.post.tags.all()) > 0:
                                tags_list_of_liked_post = like.post.tags.all()
                                tags_of_reacted_page_posts = tags_of_reacted_page_posts.union(
                                    tags_list_of_liked_post, all=True)
                        if len(tags_of_reacted_page_posts) > 0:
                            tags_id_of_reacted_page_posts = list(
                                tags_of_reacted_page_posts.values_list('pk', flat=True))
                            most_liked_tag_id = max(
                                set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                            most_liked_tags_id_list.append(
                                most_liked_tag_id)
                            while most_liked_tag_id in tags_id_of_reacted_page_posts:
                                tags_id_of_reacted_page_posts.remove(
                                    most_liked_tag_id)
                            if len(tags_id_of_reacted_page_posts) > 0:
                                second_most_liked_tag_id = max(
                                    set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                                most_liked_tags_id_list.append(
                                    second_most_liked_tag_id)
                                while second_most_liked_tag_id in tags_id_of_reacted_page_posts:
                                    tags_id_of_reacted_page_posts.remove(
                                        second_most_liked_tag_id)
                                if len(tags_id_of_reacted_page_posts) > 0:
                                    third_most_liked_tag_id = max(
                                        set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                                    most_liked_tags_id_list.append(
                                        third_most_liked_tag_id)
                            for tag_id in most_liked_tags_id_list:
                                hash_tag_instance = HashTag.objects.prefetch_related(
                                    'posts').get(tag_id=tag_id)
                                tagged_page_posts_of_instance = hash_tag_instance.posts.filter(
                                    posted_at__gte=timezone.now() - timedelta(days=2)).exclude(page__isnull=True)
                                tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.union(
                                    tagged_page_posts_of_instance)
                    tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.difference(
                        recently_suggested_posts, unknown_page_posts_to_be_suggested, page_posts_to_be_suggested)
                    if len(tagged_page_posts_to_be_suggested) >= required_number_of_posts:
                        tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.order_by(
                            '-score')[0:required_number_of_posts]
                        suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                            page_posts_to_be_suggested, tagged_page_posts_to_be_suggested)
                        user_interest.posts_to_be_suggested.set(list(suggested_posts))
                        user_interest.suggested_at = datetime.now()
                        user_interest.save()
                        return suggested_posts
                        # level 3 of page posts suggestions completed.
                    else:
                        '''
                        Posts by users, which has same hashtags as the user recently liked 10 posts, calculated based on top 3 tags most used, posted within 2 days are listed.
                        '''
                        required_number_of_posts = required_number_of_posts - \
                            len(tagged_page_posts_to_be_suggested)
                        tagged_user_posts_to_be_suggested = Post.objects.none()
                        if len(most_liked_tags_id_list) > 0:
                            for tag_id in most_liked_tags_id_list:
                                hash_tag_instance = HashTag.objects.prefetch_related(
                                    'posts').get(tag_id=tag_id)
                                tagged_user_posts_of_instance = hash_tag_instance.posts.filter(posted_at__gte=timezone.now(
                                ) - timedelta(days=2)).filter(page__isnull=True).filter(who_can_see='Public')
                                tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.union(
                                    tagged_user_posts_of_instance)
                        tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.difference(
                            recently_suggested_posts, unknown_user_posts_to_be_suggested, user_posts_to_be_suggested)
                        if len(tagged_user_posts_to_be_suggested) >= required_number_of_posts:
                            tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.order_by(
                                '-score')[0:required_number_of_posts]
                            suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested)
                            user_interest.posts_to_be_suggested.set(list(suggested_posts))
                            user_interest.suggested_at = datetime.now()
                            user_interest.save()
                            return suggested_posts
                            # level 3 of posts by user suggestions is completed.
                        else:
                            '''
                            Posts by those pages which have same fields as user has selected his favourite field are being listed.
                            '''
                            required_number_of_posts = required_number_of_posts - \
                                len(tagged_user_posts_to_be_suggested)
                            requesting_sb_user_fields = requesting_sb_user.favourite_fields.all()
                            favourite_field_top_pages = Page.objects.none()
                            for field in requesting_sb_user_fields:
                                field_page_instance = FieldPages.objects.prefetch_related(
                                    'pages').get(field=field)
                                if field_page_instance.pages.count() > 3:
                                    fields_pages = field_page_instance.pages.order_by(
                                        '-number_of_followers')[0:3]
                                else:
                                    fields_pages = field_page_instance.pages.all()
                                favourite_field_top_pages = favourite_field_top_pages.union(
                                    fields_pages)
                            if len(favourite_field_top_pages) > 5:
                                favourite_field_top_pages = favourite_field_top_pages.order_by(
                                    '-number_of_followers')[0:5]
                            favourite_field_top_posts = Post.objects.none()
                            for page in favourite_field_top_pages:
                                post_page_list_instance = PagePostList.objects.prefetch_related(
                                    'posts').get(page=page)
                                post_list_by_page = post_page_list_instance.posts.filter(
                                    posted_at__gte=timezone.now() - timedelta(days=2))
                                favourite_field_top_posts = favourite_field_top_posts.union(
                                    post_list_by_page)
                            favourite_field_top_posts = favourite_field_top_posts.difference(
                                recently_suggested_posts, tagged_page_posts_to_be_suggested, unknown_page_posts_to_be_suggested, page_posts_to_be_suggested)
                            if len(favourite_field_top_posts) >= required_number_of_posts:
                                '''
                                If i number of posts are not obtained send the posts which has been obtained.
                                It will be front end which will call for suggestion for pages and profile when empty list is returned.
                                '''
                                favourite_field_top_posts = favourite_field_top_posts.order_by(
                                    '-score')[0:required_number_of_posts]
                                suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                    page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested, favourite_field_top_posts)
                                user_interest.posts_to_be_suggested.set(list(suggested_posts))
                                user_interest.suggested_at = datetime.now()
                                user_interest.save()
                                return suggested_posts
                                # level4 of posts by page suggestions completed.
                            else:
                                suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                    page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested, favourite_field_top_posts)
                                user_interest.posts_to_be_suggested.set(list(suggested_posts))
                                user_interest.suggested_at = datetime.now()
                                user_interest.save()
                                return suggested_posts
                                # last level completed.

@shared_task(bind=True)
def get_post_suggestions(self, *args, **kwargs):
    userid = kwargs['userid']
    user_interest = UserInterest.objects.only('suggested_posts').get(user_id = userid)
    suggested_posts = kwargs['suggested_posts']
    for post in suggested_posts:
        user_interest.suggested_posts.add(post)
    post_suggestions(userid=userid)
    return "Done"

def profile_suggestions(userid):
    def count_mutual_friends(sbuser1, sbuser2):
        friend_list_of_user1 = sbuser1.friends.all()
        friend_list_of_user2= sbuser2.friends.all()
        mutual_friends = friend_list_of_user1.intersection(friend_list_of_user2)
        return len(mutual_friends)
    i = 10
    requesting_userid = userid
    requesting_sb_user = SBUser.objects.prefetch_related(
        'friends').get(user_id=requesting_userid)
    friends_list = requesting_sb_user.friends.all()
    user_interest = UserInterest.objects.get(user_id = userid)
    recently_suggested_profiles = user_interest.suggested_profiles.all()
    mutual_friends_tuple_set = set()
    #Deleting the records of profile suggestions made two days ago.
    user_interest.suggested_profiles.through.objects.filter(suggested_at__lt = timezone.now()-timedelta(days=2)).delete()
    if len(friends_list) > 0:
        for friend in friends_list:
            frnd_list_of_frnd = friend.friends.all()
            frnd_list_of_frnd = frnd_list_of_frnd.difference(recently_suggested_profiles)
            if len(frnd_list_of_frnd) > 0:
                for sbuser2 in frnd_list_of_frnd:
                    number_of_mf = count_mutual_friends(sbuser1=requesting_sb_user, sbuser2=sbuser2)
                    if number_of_mf > 0:
                        mutual_friends_tuple_set = mutual_friends_tuple_set.add((sbuser2, number_of_mf))
    if len(mutual_friends_tuple_set) >= i:
        def key(ele):
            return ele[1]
        mutual_friends_tuple_list = list(mutual_friends_tuple_set)
        mutual_friends_tuple_list.sort(key=key)
        required_tuples = mutual_friends_tuple_list[0:i]
        suggested_mf_list = [ele[0] for ele in required_tuples]
        user_interest.profiles_to_be_suggested.set(suggested_mf_list)
        user_interest.profiles_suggested_at = timezone.now()
        user_interest.save()
        return suggested_mf_list
    else:
        if len(mutual_friends_tuple_set)>0:
            suggested_mf_list = [ele[0] for ele in mutual_friends_tuple_set]
        else:
            suggested_mf_list = list()
        required_number_of_profiles = i - len(suggested_mf_list)
        recent_likes = user_interest.likes.filter(liked_at__gte = timezone.now() - timedelta(days=2)).order_by('-liked_at')
        profiles_recently_liked = SBUser.objects.none()
        if len(recent_likes)>0:
            for like in recent_likes:
                profiles_recently_liked = profiles_recently_liked.add(like.post.user)
            profiles_recently_liked = profiles_recently_liked.difference(recently_suggested_profiles, friends_list)
        if len(profiles_recently_liked) >=required_number_of_profiles:
            liked_profiles_to_be_suggested = profiles_recently_liked[0:required_number_of_profiles]
            suggested_profiles = liked_profiles_to_be_suggested.union(suggested_mf_list)
            user_interest.profiles_to_be_suggested.set(list(suggested_profiles))
            user_interest.profiles_suggested_at = timezone.now()
            user_interest.save()
            return suggested_profiles
        else:
            required_number_of_profiles = required_number_of_profiles - len(profiles_recently_liked)
            your_city = requesting_sb_user.your_city
            profiles_in_city = SBUser.objects.filter(your_city=your_city)
            required_profiles_in_city = profiles_in_city.difference(friends_list, recently_suggested_profiles)
            if len(required_profiles_in_city) >= required_number_of_profiles:
                required_profiles_in_city = required_profiles_in_city[0: required_number_of_profiles]
                suggested_profiles = required_profiles_in_city.union(suggested_mf_list, liked_profiles_to_be_suggested)
                user_interest.profiles_to_be_suggested.set(list(suggested_profiles))
                user_interest.profiles_suggested_at = timezone.now()
                user_interest.save()
                return suggested_profiles
            else:
                suggested_profiles = required_profiles_in_city.union(suggested_mf_list, liked_profiles_to_be_suggested)
                required_number_of_profiles = required_number_of_profiles - len(suggested_profiles)
                required_profiles = recently_suggested_profiles.difference(friends_list)
                try:
                    suggested_profiles = suggested_profiles.union(required_profiles[0:required_number_of_profiles])
                    #It means if programme does not find new profiles, it will suggest the recently suggested profiles again.
                except:
                    pass
                user_interest.profiles_to_be_suggested.set(list(suggested_profiles))
                user_interest.profiles_suggested_at = timezone.now()
                user_interest.save()
                return suggested_profiles

@shared_task(bind=True)
def get_profile_suggestions(self, *args, **kwargs):
    userid = kwargs['userid']
    user_interest = UserInterest.objects.only('suggested_profiles').get(user_id = userid)
    suggested_profiles = kwargs['suggested_profiles']
    for profile in suggested_profiles:
        user_interest.suggested_profiles.add(profile)
    profile_suggestions(userid = userid)
    return "Done"

def page_suggestions(userid):
    i = 10
    requesting_userid = userid
    requesting_sb_user = SBUser.objects.prefetch_related(
        'friends').get(user_id=requesting_userid)
    user_interest = UserInterest.objects.prefetch_related(
        'suggested_posts', 'followed_pages', 'likes').get(user_id=requesting_userid)
    pages_to_be_suggested = Page.objects.none()
    friends_list = requesting_sb_user.friends.all()
    frnds_user_id_list = list(friends_list.values_list('user_id', flat=True))
    followed_pages = user_interest.followed_pages.all()
    number_of_recent_page_post_likes = user_interest.likes.filter(
        post__page__isnull=False).count()
    recently_suggested_pages = user_interest.suggested_pages.all()
    user_interest.suggested_pages.through.objects.filter(suggested_at__lt = timezone.now()-timedelta(days=2)).delete()
    '''
    Pages which posts has been liked within his 20 likes, will be suggested.
    '''
    if number_of_recent_page_post_likes > 0:
        if number_of_recent_page_post_likes > 20:
            recent_page_likes = user_interest.likes.select_related('post').filter(
                post__page__isnull=False).order_by('-liked_at')[0:20]
        else:
            recent_page_likes = user_interest.likes.select_related(
                'post').filter(post__page__isnull=False).order_by('-liked_at')
        for like in recent_page_likes:
            pages_to_be_suggested = pages_to_be_suggested.union(
                {like.post.page})
        pages_to_be_suggested = pages_to_be_suggested.difference(
            followed_pages, recently_suggested_pages)
    if len(pages_to_be_suggested) >= i:
        pages_to_be_suggested = pages_to_be_suggested.order_by(
            '-number_of_followers')[0: i]
        user_interest.pages_to_be_suggested.set(list(pages_to_be_suggested))
        user_interest.pages_suggested_at = timezone.now()
        user_interest.save()
        return pages_to_be_suggested
    else:
        '''
        Those pages which have top 3 hashtags which are in last 10 posts liked by the user.
        '''
        required_number_of_pages = i - len(pages_to_be_suggested)
        if number_of_recent_page_post_likes > 10:
            recent_page_likes = recent_page_likes[0: 10]
        liked_tags_list = Tags.objects.none()
        for like in recent_page_likes:
            try:
                liked_tags_list = liked_tags_list.union(
                    like.post.tags.all(), all=True)
            except:
                continue
        if len(liked_tags_list) > 0:
            liked_tags_id_list = list(
                liked_tags_list.values_list('id', flat=True))
            most_liked_tagid = max(
                set(liked_tags_id_list), key=liked_tags_id_list.count)
            most_liked_tags_id_list = [most_liked_tagid]
            while most_liked_tagid in liked_tags_id_list:
                liked_tags_id_list.remove(most_liked_tagid)
            if len(liked_tags_id_list) > 0:
                second_most_liked_tag_id = max(
                    set(liked_tags_id_list), key=liked_tags_id_list.count)
                most_liked_tags_id_list.append(second_most_liked_tag_id)
                while second_most_liked_tag_id in liked_tags_id_list:
                    liked_tags_id_list.remove(second_most_liked_tag_id)
                if len(liked_tags_id_list) > 0:
                    third_most_liked_tag = max(
                        set(liked_tags_id_list), key=liked_tags_id_list.count)
                    most_liked_tags_id_list.append(third_most_liked_tag)
            for tag_id in most_liked_tags_id_list:
                hash_tag_instance = HashTag.objects.prefetch_related(
                    'pages').only('pages').get(tag_id=tag_id)
                try:
                    pages_to_be_suggested = pages_to_be_suggested.union(
                        hash_tag_instance.pages.all())
                except:
                    continue
            pages_to_be_suggested = pages_to_be_suggested.difference(followed_pages, recently_suggested_pages)
        if len(pages_to_be_suggested) >= required_number_of_pages:
            pages_to_be_suggested = pages_to_be_suggested.order_by(
                '-number_of_followers')[0: required_number_of_pages]
            user_interest.pages_to_be_suggested.set(list(pages_to_be_suggested))
            user_interest.pages_suggested_at = timezone.now()
            user_interest.save()
            return pages_to_be_suggested
        else:
            '''
            Pages whose creators are the friends of the user, are being suggested.
            '''
            required_number_of_pages = i - len(pages_to_be_suggested)
            pages_to_be_suggested = pages_to_be_suggested.union(Page.objects.filter(creator_id__in=frnds_user_id_list).order_by(
                '-number_of_followers').difference(followed_pages, recently_suggested_pages))
            if len(pages_to_be_suggested) >= required_number_of_pages:
                pages_to_be_suggested = pages_to_be_suggested[0:required_number_of_pages]
                user_interest.pages_to_be_suggested.set(list(pages_to_be_suggested))
                user_interest.pages_suggested_at = timezone.now()
                user_interest.save()
                return pages_to_be_suggested
            else:
                '''
                Pages with the fields which user also has mentioned in his bio.
                '''
                required_number_of_pages = i - len(pages_to_be_suggested)
                user_favourite_fields = requesting_sb_user.favourite_fields.all()
                field_matching_pages = Page.objects.none()
                for field in user_favourite_fields:
                    field_page_instance = FieldPages.objects.get(
                        field=field)
                    field_matching_pages = field_matching_pages.union(
                        field_page_instance.pages.all())
                pages_to_be_suggested = pages_to_be_suggested.union(field_matching_pages).difference(followed_pages, recently_suggested_pages)
                if len(field_matching_pages) >= required_number_of_pages:
                    pages_to_be_suggested = pages_to_be_suggested.order_by(-'number_of_followers')[0: required_number_of_pages]
                    user_interest.pages_to_be_suggested.set(list(pages_to_be_suggested))
                    user_interest.pages_suggested_at = timezone.now()
                    user_interest.save()
                    return pages_to_be_suggested
                else:
                    '''
                    If 10 pages are still not found, send previously suggested profiles. 
                    '''
                    required_number_of_pages = required_number_of_pages - len(pages_to_be_suggested)
                    eligible_pages = recently_suggested_pages.difference(followed_pages)
                    required_pages = eligible_pages.order_by('-number_of_followers')[0:required_number_of_pages]
                    pages_to_be_suggested = pages_to_be_suggested.union(required_pages)
                    user_interest.pages_to_be_suggested.set(list(pages_to_be_suggested))
                    user_interest.pages_suggested_at = timezone.now()
                    user_interest.save()
                    return pages_to_be_suggested

@shared_task(bind=True)
def get_page_suggestions(self, *args, **kwargs):
    userid = kwargs['userid']
    user_interest = UserInterest.objects.only('suggested_pages').get(user_id = userid)
    suggested_pages = kwargs['suggested_pages']
    for page in suggested_pages:
        user_interest.suggested_pages.add(page)
    
    page_suggestions(userid = userid)
    return "Done"

