def retrieve_post_and_comments(client, post_id):
    result = {
        'post': None,
        'most_upvoted_comment': None,
        'most_upvoted_reply': None
    }

    # Retrieve the post
    post_response = client.get_post(post_id)
    if not post_response or not post_response.title:
        return result  # Post not found

    # Add the post details to the result
    result['post'] = {
        'title': post_response.title,
        'text': post_response.text,
        'score': post_response.score,
        'state': post_response.state,
        'publication_date': post_response.publication_date
        # Include other fields as needed
    }

    # Retrieve the most upvoted comments under the post
    top_comments_response = client.get_top_comments(post_id, n=1)
    if not top_comments_response.comments:
        return result  # No comments found

    # Add the most upvoted comment details to the result
    most_upvoted_comment = top_comments_response.comments[0]
    result['most_upvoted_comment'] = {
        'text': most_upvoted_comment.text,
        'author': most_upvoted_comment.author,
        'score': most_upvoted_comment.score,
        'state': most_upvoted_comment.state,
        'publication_date': most_upvoted_comment.publication_date
        # Include other fields as needed
    }
    # Expand the comment branch to get replies to the most upvoted comment
    expanded_comment_response = client.expand_comment_branch(most_upvoted_comment.id, n=5)
    if expanded_comment_response.comments:
        # Sort the replies by score to find the most upvoted reply
        sorted_replies = sorted(expanded_comment_response.comments, key=lambda c: c.score, reverse=True)
        if sorted_replies:
            most_upvoted_reply = sorted_replies[0]
            result['most_upvoted_reply'] = {
                'id': most_upvoted_reply.id,
                'text': most_upvoted_reply.text,
                'author': most_upvoted_reply.author,
                'score': most_upvoted_reply.score,
                'state': most_upvoted_reply.state,
                'publication_date': most_upvoted_reply.publication_date
            }
    else:
        # This else block is currently setting most_upvoted_comment to None if there are no replies, which is incorrect.
        # It should only set most_upvoted_reply to None.
        result['most_upvoted_reply'] = None

    return result
