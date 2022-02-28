'''
request.META.get('REMOTE_ADDR') gives IP address of the user.
1) Use queries in an optimized way.
For foreign key, select_related,
for manytomany, prefetch_related.
Fetch as much data as you need only.
Fetch the whole data that will be used, at once instead of hitting data base again and again.
Fetch only those fields which are necessary. Use only and defer for this application.
Use count and exists instead of len and a for loop.
Never use count and exists too many times.

2) sqlite database do not support some sql commands and so some django orm's commands.
Postgres supports most of the commands of django orm.
sqlite does not support ordering and limiting like commands on subqueries of compound querysets.

4) While transferring data from json file to postgres, utf-8 decoder does not support.
5)string.strip() returns string without leading whitespace.
6)string.casefold() returns a caseless comparision of strings.
7) We can use dynamic serializer class and dynamic fields for serializers.
8) We can use dynamic querysets for a view.
9) qs.get() throws an object does not exist error if no data found. Use try and except to deal with this error.
10) qs.filter().first() gives None if no data found.
11) get_or_create returns a tuple with first element the instance and second true or false. 
12) save() is called only when an object is created or updated. Using save for auto filling values must be a carful application.
Use django celery instead, if auto filling of data is necessary.
13) Model can be related to itself with self keyword and we can define an intermediary model for the relationship.
15) Validation must be appropriate and every scenario must be considered while dealing with requests.
16)Destroy do not need serializer class and Create does not need a queryset.
17) We can merge few different deserialized data with + to send response.
'''