# SineBook
This repository has rest APIs of the major features of facebook, built on rest framework with simple jwt auth.

SB.models has following models:
  1) Page: This Model has been created for sinebook page which has features similar to the facebook page. Any authenticated user can create a page and add members who can post on the page. An authenticated user can follow the page and that user will be suggested the posts by the page in his/her post feed.
  2) SBUser: This model has been created for the profile and other actions like who can see user's personal info etc. This is simply a hybrid model for profile and profile settings.
  3) Post: This models has been created for posts which has many fields like description, image etc. The settings related to the post has also been added in the same model like user can set his post to be visible to only his friends etc. There is one more important field 'page' which has foreign key to Page model. This indicates that the posts by user and by page both are being stored in the same table. The posts by user will have page field None. One more thing that the settings like 'who_can_see' does not mean anything for posts user because views are not designed to check these fields for the posts which are posted by the user. Another important field is score which is a float field and is calculated using likes, comments and shares of the post, this score decides the virality of the post.
  4) Tag and HashTag models: These are important models which deals with the tag written in the post description as well as tags in the page profile. Tag is automatically created whenever any post description tags anything and HashTag model takes the foreign key to the tag and put that page or post in that hashtag.
  5) UserInterest: This model has all the info about the posts by the user, posts liked by the user, posts shared by the user, posts on which user has commented, posts, pages and profile, which has been suggested to the user or have to be suggested. These 'to_be_suggested' fields are being updated using celery and signals.
  6) There are more models like PagePostList which has the list of posts by the page, FieldPages which has the list of pages of a particular fields and models like Like, Comment, PostShare are also there. Comment has the foreign key to the self which means users can comment on the comments also.
  
SB.tasks has following important functions:
  1) post_suggestion(userid): This fuction takes userid as input and return 10 posts which are to be suggested as well as stores them in the 'posts_to_be_suggested' in the UserInterest model. This function has following stages:
  
      a) This function tries to find the posts, posted by the friends within last two days, which are not in the 'suggested_posts' of UserInterest. If it gets 10 such posts, it immediately saves them in the posts_to_be_suggested column of the UserInterest model. If it does not find 10 posts, it forwards to next stage.

      b) In this stage, it tries to find the posts by the pages, which are followed by the user and the posts are not in the 'suggested_posts'. If these completes the quota of 10 posts, it saves them and returns immediately else it forwards to next stage.
      
      c) In this stage, it tries to find those posts by the pages whose posts has recently been liked and are not in the 'suggested_posts'. If these completes the quota of 10, it saves them and returns immediately else it forwards to next stage.
      
      d) In this stage, it tries to find those posts by the users whose posts has recently been liked and are not in the 'suggested_posts'. If these completes the quota of 10, it saves them and returns immediately else it forwards to next stage.
      
      e) In this stage, it tries to find the top posts by the pages, with the hashtags whose posts has been liked by the user most and are not in the 'suggested_posts'. If these completes the quota of 10, it saves them and returns immediately else it forwards to next stage.
      
      f) In this stage, it tries to find the top posts by the users, with the hashtags whose posts has been liked by the user most and are not in the 'suggested_posts'. If these completes the quota of 10, it saves them and returns immediately else it forwards to next stage.
      
      g) In this stage, it tries to find the posts by the pages which has same fields which user has specified as favourite fields in his profile. If these completes the quota of 10, it saves them and returns immediately else it returns the posts which it found till now.

  2) page_suggestions(userid): This function takes userid as input and returns 10 pages that are to be suggested as well as saves them in the 'pages_to_be_suggested' field of the model UserInterest.
  
      a) It tries to find those pages whose posts has been liked by the user within his last 20 likes and are different from the 'suggested_pages' and 'followed_pages'. If quota of 10 if filled, it immediately returns those 10 pages else it forwards to next step.
      
      b) In this stage, it finds top pages with the tags whose posts has been liked most by the user recently as well as these pages are different from 'suggested_pages' and 'followed_pages'. If quota of 10 if filled, it immediately returns those 10 pages else it forwards to next step.
      
      c) In this stage, it find pages whose creators are the user's friends and these pages are different from 'suggested_pages' and 'followed_pages'. If quota of 10 if filled, it immediately returns those 10 pages else it forwards to next step.
      
      d) In this stage, it finds the pages with the same fields which user has mentioned as favourite fields in his profile and these pages are different from 'suggested_pages' and 'followed_pages'. If quota of 10 if filled, it immediately returns those 10 pages else it returns pages from the 'suggested_posts' to fill the quota.
      
  3) profile_suggestions(userid): This suggests profiles to user for friend request. It takes userid as input and returns 10 profiles.
  
      a) First of all, it finds users with mutual friends and suggests top 10 profiles from them and are different from the 'suggested_profiles'. If quota of 10 is filled then it returns those profiles else forwards to next step.
      
      b) In this stage, it suggests those users whose posts has recently been liked by the user and are different from the 'suggested_profiles'. If quota of 10 is filled then it returns those profiles else forwards to next step.
      
      c) In this stage, it suggests those users which are from same city from which user is and and are different from the 'suggested_profiles'. If quota of 10 is filled then it returns those profiles else fills the quoata with 'suggested_profiles'.
