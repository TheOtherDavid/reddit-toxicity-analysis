from reddit import get_top_threads, get_comments_for_thread
from db import connect, close, Subreddits, Threads, Comments

# Replace these with your subreddit and thread count

num_threads_to_retrieve = 10
num_comments_to_retrieve_per_thread = 10  # Adjust this value

def get_comments_for_subreddit(subreddit_name):
    # Fetch the top threads from Reddit
    top_threads = get_top_threads(subreddit_name, num_threads_to_retrieve)
    print("Retrieved threads.")
    # Connect to the database
    db_connection = connect()

    if db_connection:
        try:
            # Create a Subreddits object for the subreddit
            subreddits_repo = Subreddits(db_connection)

            # Check if the subreddit exists in the database, and create it if not
            subreddit_info = subreddits_repo.get_subreddit_by_name(subreddit_name)
            if not subreddit_info:
                subreddit_id = subreddits_repo.create_subreddit(subreddit_name)
            else:
                subreddit_id = subreddit_info['subreddit_id']

            # Create a Threads object for storing thread data
            threads_repo = Threads(db_connection)

            # Create a Comments object for storing comment data
            comments_repo = Comments(db_connection)

            # Save each top thread to the database
            for thread in top_threads:
                #Save to DB
                thread_db_id = threads_repo.create_thread(subreddit_id, thread['thread_title'], '', None, 0, None)
                comments = get_comments_for_thread(subreddit_name, thread['thread_id'], num_comments_to_retrieve_per_thread)
                for comment in comments:
                    #Save to DB
                    comments_repo.create_comment(thread_db_id, comment['comment_text'], None, None, 0, None, None, None, None)
                print("Saved comments for thread.")
            print("Complete.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the database connection
            close(db_connection)

if __name__ == '__main__':
    subreddit_name = 'flashlight'
    get_comments_for_subreddit(subreddit_name)
