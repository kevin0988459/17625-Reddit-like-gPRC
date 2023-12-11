import grpc
from protos import reddit_pb2
from protos import reddit_pb2_grpc

class RedditClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = reddit_pb2_grpc.RedditServiceStub(self.channel)

    def create_post(self, title, text, video_url=None, image_url=None):
        post_request = reddit_pb2.CreatePostRequest(
            title=title, text=text, video_url=video_url, image_url=image_url)
        return self.stub.CreatePost(post_request)

    def vote_post(self, post_id, upvote):
        vote_request = reddit_pb2.VotePostRequest(post_id=post_id, upvote=upvote)
        return self.stub.VotePost(vote_request)

    def get_post(self, post_id):
        get_post_request = reddit_pb2.GetPostRequest(post_id=post_id)
        return self.stub.GetPost(get_post_request)

    def create_comment(self, post_id, author, text):
        comment_request = reddit_pb2.CreateCommentRequest(
            post_id=post_id, author=author, text=text)
        return self.stub.CreateComment(comment_request)

    def vote_comment(self, comment_id, upvote):
        vote_request = reddit_pb2.VoteCommentRequest(comment_id=comment_id, upvote=upvote)
        return self.stub.VoteComment(vote_request)

    def get_top_comments(self, post_id, n):
        top_comments_request = reddit_pb2.GetTopCommentsRequest(post_id=post_id, n=n)
        return self.stub.GetTopComments(top_comments_request)

    def expand_comment_branch(self, comment_id, n):
        expand_request = reddit_pb2.ExpandCommentBranchRequest(comment_id=comment_id, n=n)
        return self.stub.ExpandCommentBranch(expand_request)

    def close(self):
        self.channel.close()


client = RedditClient(host='localhost', port=50051)


# Close the client when done
client.close()
