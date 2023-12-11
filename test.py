import unittest
from unittest.mock import MagicMock
from high_level_function import retrieve_post_and_comments
from protos import reddit_pb2  # Make sure to import reddit_pb2

class TestRetrievePostAndComments(unittest.TestCase):
    def test_retrieve_post_and_comments(self):
        # Create a mock RedditClient
        mock_client = MagicMock()

        # Define what the mock should return when get_post and get_top_comments are called
        mock_client.get_post.return_value = MagicMock(
            title='Big news',
            text='Shohei is going to Dodgers',
            score=80090,
            state=reddit_pb2.Post.NORMAL,
            publication_date='2023-12-01 12:00:00',
            video_url=None,
            image_url='image1.jpg'
        )

        mock_client.get_top_comments.return_value = MagicMock(
            comments=[MagicMock(
                id=1,
                text='What?',
                author='u1',
                score=1230,
                state=reddit_pb2.Comment.NORMAL,
                publication_date='2023-12-01 13:00:00',
                parent_post_id=1,
                parent_comment_id=None
            )]
        )

        mock_client.expand_comment_branch.return_value = MagicMock(comments=[])

        # Call the function with the mock client
        result = retrieve_post_and_comments(mock_client, post_id=1)
        # Check if the function returns the expected result
        self.assertIsNotNone(result['post'])
        self.assertEqual(result['post']['title'], 'Big news')  
        self.assertIsNotNone(result['most_upvoted_comment'])
        self.assertEqual(result['most_upvoted_comment']['text'], 'What?')  
        self.assertIsNone(result['most_upvoted_reply'])  

if __name__ == '__main__':
    unittest.main()
