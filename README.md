# SineBook
This repository has rest APIs of the major features of facebook, built on rest framework with simple jwt auth.

SB.models has following models:
  1) Page: This Model has been created for sinebook page which has features similar to the facebook page. Any authenticated user can create a page and add members who can post on the page. An authenticated user can follow the page and that user will be suggested the posts by the page in his/her post feed.
  2) SBUser: This model has been created for the profile and other actions like who can see user's personal info etc. This is simply a hybrid model for profile and profile settings.
  3) Post: This models has been created for posts which has many fields like description, image etc. The settings related to the post has also been added in the same model like user can set his post to be visible to only his friends etc. There is one more important field 'page' which has foreign key to Page model. This indicates that the posts by user and by page both are being stored in the same table. The posts by user will have page field None. One more thing that the settings like 'who_can_see' does not mean anything for posts user because views are not designed to check these fields for the posts which are posted by the user. Another important field is score which is a float field and is calculated using likes, comments and shares of the post, this score decides the virality of the post.
  4) Tag and HashTag models: These are important models which deals with the tag written in the post description as well as tags in the page profile. Tag is automatically created whenever any post description tags anything and HashTag model takes the foreign key to the tag and put that page or post in that hashtag.
  5) UserInterest: This model has all the info about the posts by the user, posts liked by the user, posts shared by the user, posts on which user has commented, posts, pages and profile, which has been suggested to the user or have to be suggested. These 'to_be_suggested' fields are being updated using celery and signals.
  6) There are more models like PagePostList which has the list of posts by the page, FieldPages which has the list of pages of a particular fields and models like Like, Comment, PostShare are also there. Comment has the foreign key to the self which means users can comment on the comments also.
  
  
