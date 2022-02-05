# Generated by Django 4.0.2 on 2022-02-05 06:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavouriteField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked_at', models.DateTimeField(auto_now=True)),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-liked_at'],
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SBUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('date_of_birth', models.DateField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('your_first_school', models.CharField(blank=True, max_length=255, null=True)),
                ('your_college', models.CharField(blank=True, max_length=255, null=True)),
                ('your_occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('your_address', models.CharField(blank=True, max_length=255, null=True)),
                ('favourite_movies', models.CharField(blank=True, max_length=255, null=True)),
                ('favourite_books', models.CharField(blank=True, max_length=255, null=True)),
                ('tell_your_friends_about_you', models.TextField(blank=True, max_length=500, null=True)),
                ('display_email', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('display_mobile', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='None', max_length=255)),
                ('display_personal_info', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('display_friends', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('favourite_fields', models.ManyToManyField(blank=True, related_name='user_favourite_fields', to='SB.FavouriteField')),
                ('friends', models.ManyToManyField(blank=True, to='SB.SBUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=200, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('who_can_see', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('who_can_comment', models.CharField(choices=[('Public', 'Public'), ('Friends', 'Friends'), ('None', 'None')], default='Public', max_length=255)),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('likes', models.ManyToManyField(blank=True, related_name='liking_users', through='SB.Like', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=5000)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_creator', to=settings.AUTH_USER_MODEL)),
                ('fields', models.ManyToManyField(related_name='page_related_fields', to='SB.FavouriteField')),
                ('followers', models.ManyToManyField(blank=True, related_name='page_followers', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='page_members', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(blank=True, related_name='page_tags', to='SB.Tags')),
            ],
        ),
        migrations.CreateModel(
            name='LikedOrCommentedPosts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('followed_pages', models.ManyToManyField(blank=True, related_name='followed_pages', to='SB.Page')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liker_or_commentor', to=settings.AUTH_USER_MODEL)),
            ],
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
                ('tag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='SB.tags')),
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
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=255)),
                ('commented_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comment_on_which_user_can_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_object', to='SB.comment')),
                ('likes', models.ManyToManyField(blank=True, related_name='comment_likers', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SB.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-commented_at'],
            },
        ),
    ]
