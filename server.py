import grpc
from concurrent import futures
from protos import reddit_pb2
from protos import reddit_pb2_grpc
from datetime import datetime

# Mock data structures
posts = {
    1: {
        "title": "Big news",
        "text": "Shohei is going to Dodgers",
        "video_url": None,
        "image_url": "image1.jpg",
        "score": 80090,
        "state": reddit_pb2.Post.NORMAL,
        "publication_date": "2023-12-01 12:00:00",
        "comments": [1, 2]
    },
    2: {
        "title": "MSE number 1",
        "text": "MSE is so good",
        "video_url": "video1.mp4",
        "image_url": None,
        "score": 20,
        "state": reddit_pb2.Post.NORMAL,
        "publication_date": "2022-01-02 13:00:00",
        "comments": []
    }
}

comments = {
    1: {
        "text": "What?",
        "author": "u1",
        "score": 1230,
        "state": reddit_pb2.Comment.NORMAL,
        "publication_date": "2023-12-01 13:00:00",
        "parent_post_id": 1,
        "parent_comment_id": None 
    },
    2: {
        "text": "so nice",
        "author": "u2",
        "score": 2,
        "state": reddit_pb2.Comment.NORMAL,
        "publication_date": "2023-12-05 14:00:00",
        "parent_post_id": 1,
        "parent_comment_id": None 
    },
    3: {
        "text": "sub-reply",
        "author": "u2",
        "score": 300,
        "state": reddit_pb2.Comment.NORMAL,
        "publication_date": "2023-12-03 14:00:00",
        "parent_post_id": 1,
        "parent_comment_id":1 
    }
    
}

comment_id_counter = 3
post_id_counter = 3

class RedditServiceImpl(reddit_pb2_grpc.RedditServiceServicer):
    def CreatePost(self, request, context):
        global post_id_counter
        post_id = post_id_counter
        post_id_counter += 1

        # Create and store the post with all relevant fields
        posts[post_id] = {
            "title": request.title,
            "text": request.text,
            "video_url": request.video_url if request.video_url else None,
            "image_url": request.image_url if request.image_url else None,
            "score": 0,  # Default score
            "state": reddit_pb2.Post.NORMAL,  # Default state as NORMAL
            "publication_date": str(datetime.now()),  # Current date as publication date
            "comments": []  # List to store comment IDs
        }
        return reddit_pb2.CreatePostResponse(post_id=post_id)

    def VotePost(self, request, context):
        if request.post_id in posts:
            posts[request.post_id]["score"] += 1 if request.upvote else -1
            return reddit_pb2.VoteResponse(success=True)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return reddit_pb2.VoteResponse(success=False)


    def GetPost(self, request, context):
        if request.post_id in posts:
            post = posts[request.post_id]
            
            # Prepare the Post response
            post_response = reddit_pb2.Post(
                title=post["title"], 
                text=post["text"], 
                score=post["score"],
                state=post["state"],
                publication_date=post["publication_date"]
            )

            # Set the appropriate field in the oneof 'multimedia' group
            if "video_url" in post and post["video_url"]:
                post_response.video_url = post["video_url"]
            elif "image_url" in post and post["image_url"]:
                post_response.image_url = post["image_url"]

            return post_response
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return reddit_pb2.Post()



    def CreateComment(self, request, context):
        global comment_id_counter
        comment_id = comment_id_counter
        comment_id_counter += 1

        # Create and store the comment with a default state of NORMAL
        comments[comment_id] = {
            "text": request.text,
            "author": request.author,
            "score": 0,  # Default score
            "state": reddit_pb2.Comment.NORMAL,  # Set the state to NORMAL
            "publication_date": str(datetime.now()),  # Set the current time as the publication date
            "parent_post_id": request.post_id
        }

        # Link comment to the post
        if request.post_id in posts:
            posts[request.post_id]["comments"].append(comment_id)

        return reddit_pb2.CreateCommentResponse(comment_id=comment_id)


    def VoteComment(self, request, context):
        if request.comment_id in comments:
            comments[request.comment_id]["score"] += 1 if request.upvote else -1
            return reddit_pb2.VoteResponse(success=True)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Comment not found')
            return reddit_pb2.VoteResponse(success=False)


    def GetTopComments(self, request, context):
        if request.post_id in posts:
            post_comments = posts[request.post_id]["comments"]
            sorted_comments = sorted(post_comments, key=lambda id: comments[id]["score"], reverse=True)
            top_comments = sorted_comments[:request.n]
            # Build Comment objects using all fields from the Comment message definition
            comments_list = [
                reddit_pb2.Comment(
                    id=id,
                    text=comments[id]["text"],
                    author=comments[id]["author"],
                    score=comments[id]["score"],
                    state=comments[id]["state"],
                    publication_date=comments[id]["publication_date"],
                    parent_post_id=comments[id]["parent_post_id"]
                ) for id in top_comments
            ]
            return reddit_pb2.TopCommentsResponse(comments=comments_list)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return reddit_pb2.TopCommentsResponse()


    def ExpandCommentBranch(self, request, context):
        if request.comment_id in comments:
            # Initialize an empty list for replies
            replies = []

            # Find all replies to this comment
            for id, comment in comments.items():
                if comment["parent_comment_id"] == request.comment_id:
                    reply_obj = reddit_pb2.Comment(
                        id=id,
                        text=comment["text"],
                        author=comment["author"],
                        score=comment["score"],
                        state=comment["state"],
                        publication_date=comment["publication_date"],
                        parent_post_id=comment["parent_post_id"]
                    )
                    replies.append(reply_obj)

            # Return only the replies, not including the main comment
            return reddit_pb2.CommentBranchResponse(comments=replies)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Comment not found')
            return reddit_pb2.CommentBranchResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditServiceImpl(), server)
    server.add_insecure_port('[::]:50051')
    print("Server started at [::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()



