# Generated by Django 3.2.12 on 2022-03-03 07:18

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=255)),
                ('number_of_likes', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('commented_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment_on_which_user_can_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_object', to='SB.comment')),
                ('likes', models.ManyToManyField(blank=True, related_name='comment_likers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FavouriteField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked_at', models.DateTimeField(auto_now=True)),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=5000)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('number_of_followers', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_creator', to=settings.AUTH_USER_MODEL)),
                ('fields', models.ManyToManyField(related_name='page_related_fields', to='SB.FavouriteField')),
                ('followers', models.ManyToManyField(blank=True, related_name='page_followers', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='page_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=200, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('number_of_likes', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_comments', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('number_of_shares', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('effective_number_of_comments', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('who_can_see', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('who_can_comment', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('score', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('likes', models.ManyToManyField(blank=True, related_name='liking_users', through='SB.Like', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posting_page', to='SB.page')),
                ('shared_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sharing_post', to='SB.post')),
            ],
        ),
        migrations.CreateModel(
            name='PostShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_at', models.DateTimeField(auto_now_add=True)),
                ('shared_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_shared', to='SB.post')),
                ('sharing_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_sharing', to='SB.post')),
            ],
        ),
        migrations.CreateModel(
            name='SBUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('date_of_birth', models.DateField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('your_school', models.CharField(blank=True, max_length=255, null=True)),
                ('your_college', models.CharField(blank=True, max_length=255, null=True)),
                ('your_occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('your_city', models.CharField(blank=True, max_length=255, null=True)),
                ('favourite_movies', models.CharField(blank=True, max_length=255, null=True)),
                ('favourite_books', models.CharField(blank=True, max_length=255, null=True)),
                ('tell_your_friends_about_you', models.TextField(blank=True, max_length=500, null=True)),
                ('display_email', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('display_mobile', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='None', max_length=255)),
                ('display_personal_info', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('display_friends', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('favourite_fields', models.ManyToManyField(related_name='user_favourite_fields', to='SB.FavouriteField')),
                ('friends', models.ManyToManyField(blank=True, related_name='_SB_sbuser_friends_+', to='SB.SBUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SuggestedPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_at', models.DateTimeField(auto_now_add=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggested_page_to_user', to='SB.page')),
            ],
        ),
        migrations.CreateModel(
            name='SuggestedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggested_post_to_user', to='SB.post')),
            ],
        ),
        migrations.CreateModel(
            name='SuggestedProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggested_profile_to_user', to='SB.sbuser')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_at', models.DateTimeField()),
                ('profiles_suggested_at', models.DateTimeField()),
                ('pages_suggested_at', models.DateTimeField()),
                ('comments', models.ManyToManyField(blank=True, related_name='commented_posts', to='SB.Comment')),
                ('followed_pages', models.ManyToManyField(blank=True, related_name='followed_pages', to='SB.Page')),
                ('likes', models.ManyToManyField(blank=True, related_name='liked_posts', to='SB.Like')),
                ('pages_to_be_suggested', models.ManyToManyField(blank=True, related_name='to_be_suggested_pages', to='SB.Page')),
                ('posts', models.ManyToManyField(blank=True, related_name='posting_user', to='SB.Post')),
                ('posts_to_be_suggested', models.ManyToManyField(blank=True, related_name='to_be_suggested_posts', to='SB.Post')),
                ('profiles_to_be_suggested', models.ManyToManyField(blank=True, related_name='to_be_suggested_profiles', to='SB.SBUser')),
                ('shares', models.ManyToManyField(blank=True, related_name='shares', to='SB.PostShare')),
                ('suggested_pages', models.ManyToManyField(blank=True, related_name='suggested_pages', through='SB.SuggestedPage', to='SB.Page')),
                ('suggested_posts', models.ManyToManyField(blank=True, related_name='suggested_posts', through='SB.SuggestedPost', to='SB.Post')),
                ('suggested_profiles', models.ManyToManyField(blank=True, related_name='suggested_profiles', through='SB.SuggestedProfile', to='SB.SBUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='liker_or_commentor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='suggestedprofile',
            name='user_interest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_interest_instance_for_profiles', to='SB.userinterest'),
        ),
        migrations.AddField(
            model_name='suggestedpost',
            name='user_interest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_interest_instance_for_posts', to='SB.userinterest'),
        ),
        migrations.AddField(
            model_name='suggestedpage',
            name='user_interest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_interest_instance_for_pages', to='SB.userinterest'),
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='post_tags', to='SB.Tags'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='PagePostList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='page_with_posts', to='SB.page')),
                ('posts', models.ManyToManyField(blank=True, related_name='posts_of_page', to='SB.Post')),
            ],
        ),
        migrations.AddField(
            model_name='page',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='page_tags', to='SB.Tags'),
        ),
        migrations.AddField(
            model_name='like',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SB.post'),
        ),
        migrations.CreateModel(
            name='HashTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pages', models.ManyToManyField(blank=True, related_name='tagged_pages', to='SB.Page')),
                ('posts', models.ManyToManyField(blank=True, related_name='tagged_posts', to='SB.Post')),
                ('tag', models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='SB.tags')),
            ],
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sine_book_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FieldPages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='page_field', to='SB.favouritefield')),
                ('pages', models.ManyToManyField(blank=True, related_name='field_pages', to='SB.Page')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SB.post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
