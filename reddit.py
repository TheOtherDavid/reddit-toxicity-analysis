import praw
from dotenv import load_dotenv
import os

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, 
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT)

def get_top_threads(subreddit_name, num_threads):
    subreddit = reddit.subreddit(subreddit_name)

    top_threads = []

    for submission in subreddit.top(time_filter='week', limit=num_threads):
        thread_info = {
            'thread_id': submission.id,
            'thread_title': submission.title,
            'thread_text': submission.selftext  # You can include additional information as needed
        }
        top_threads.append(thread_info)

    return top_threads

def get_comments_for_thread(subreddit_name, thread_id, num_comments):
    subreddit = reddit.subreddit(subreddit_name)

    comments = []

    try:
        submission = reddit.submission(id=thread_id)

        submission.comments.replace_limit = num_comments
        #submission.comments.refresh()
        for comment in submission.comments:
            comment_info = {
                'comment_id': comment.id,
                'comment_text': comment.body,
                'comment_author': comment.author  # Include additional information like author
            }
            comments.append(comment_info)
            #Only get num_comments comments
            if len(comments) >= num_comments:
                break

        return comments

    except Exception as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list on error