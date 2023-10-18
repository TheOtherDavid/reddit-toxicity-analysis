from db import connect, close, Subreddits, Threads, Comments, SentimentScores
from gpt import get_gpt_sentiment_analysis
#Perform sentiment analysis on a subreddit
#Structure:
#Get threads from DB
#For each thread, get comments from DB
#For each comment, run sentiment analysis on that comment
#Save sentiment analysis results to DB
#Once all comments are done for a thread, average those scores and save the thread score to DB
#Once all threads are done for a subreddit, average those scores and save the subreddit score to DB

def run_analysis_for_subreddit(subreddit_name):
    # Connect to the database
    db_connection = connect()

    if db_connection:
        try:
            subreddits_repo = Subreddits(db_connection)

            subreddit_info = subreddits_repo.get_subreddit_by_name(subreddit_name)
            if not subreddit_info:
                #throw error, subreddit not found
                print("Subreddit not found")
                return
            else:
                subreddit_id = subreddit_info['subreddit_id']

            threads_repo = Threads(db_connection)
            comments_repo = Comments(db_connection)
            sentiment_scores_repo = SentimentScores(db_connection)

            threads = threads_repo.get_threads_by_subreddit_id(subreddit_id)

            for thread in threads:
                thread_id = thread['thread_id']
                comments = comments_repo.get_comments_by_thread_id(thread_id)

                # For each comment, run sentiment analysis
                for comment in comments:
                    comment_content = comment['comment_content']
                    try:
                        sentiment_scores = get_gpt_sentiment_analysis(comment_content)
                        sentiment_score = sentiment_scores['comment_sentiment_score']
                        score_confidence = sentiment_scores['score_confidence']
                    except Exception as e:
                        print(f"Error: {e}. Error for comment: '" + comment_content + "'. Skipping to the next record.")
                        continue
                    # Save sentiment analysis to DB
                    sentiment_scores_repo.create_sentiment_score(comment['comment_id'], sentiment_score, score_confidence)
                print("Sentiment analysis for thread complete.")
            print("Sentiment analysis for subreddit complete.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the database connection
            close(db_connection)


def sum_up_scores_for_subreddit(subreddit_name):
    print(f"Beginning sum job.")
    db_connection = connect()
    subreddits_repo = Subreddits(db_connection)
    threads_repo = Threads(db_connection)

    comments_repo = Comments(db_connection)

    sentiment_scores_repo = SentimentScores(db_connection)

    # Check if the subreddit exists in the database, and create it if not
    subreddit_info = subreddits_repo.get_subreddit_by_name(subreddit_name)
    if not subreddit_info:
        #throw error, subreddit not found
        print("Subreddit not found")
        return
    else:
        subreddit_id = subreddit_info['subreddit_id']

    # Get all threads for the subreddit name
    threads = threads_repo.get_threads_by_subreddit_id(subreddit_id)
    for thread in threads:
        # Once all comments are done for a thread, average those scores and save the thread score to DB
        # Join the comment table with the sentiment score table by comment ID, and use the thread ID to get the average
        thread_score = sentiment_scores_repo.get_average_sentiment_score_by_thread_id(thread['thread_id'])
        threads_repo.update_thread_sentiment_score(thread['thread_id'], thread_score)

        # Once all threads are done for a subreddit, average those scores and save the subreddit score to DB
        subreddit_score = threads_repo.get_average_sentiment_score_by_subreddit_id(subreddit_id)
        subreddits_repo.update_subreddit_sentiment_score(subreddit_id, subreddit_score)

if __name__ == '__main__':
    subreddit_name = 'flashlight'
    run_analysis_for_subreddit(subreddit_name)
    sum_up_scores_for_subreddit(subreddit_name)
