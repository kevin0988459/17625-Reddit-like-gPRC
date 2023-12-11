from client import RedditClient  
from high_level_function import retrieve_post_and_comments

client = RedditClient()
result = retrieve_post_and_comments(client, post_id=1)
print(result)
