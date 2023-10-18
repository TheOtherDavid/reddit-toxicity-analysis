import os
import psycopg2
import psycopg2.extras  # Import DictCursor from psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# Database connection settings
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DB = os.environ['POSTGRES_DB']

# Set up a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=2,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    dbname=POSTGRES_DB
)


# Define functions for establishing and closing database connections
def connect():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def close(conn):
    if conn:
        conn.close()

class Subreddits:
    def __init__(self, connection):
        self.connection = connection

    def create_subreddit(self, subreddit_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Subreddits (subreddit_name) VALUES (%s) RETURNING subreddit_id",
                (subreddit_name,)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def get_subreddit_by_name(self, subreddit_name):
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM Subreddits WHERE subreddit_name = %s",
                (subreddit_name,)
            )
            return cursor.fetchone()
    
    def update_subreddit_sentiment_score(self, subreddit_id, sentiment_score):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Subreddits SET subreddit_sentiment_score = %s WHERE subreddit_id = %s",
                (sentiment_score, subreddit_id)
            )
            self.connection.commit()

    # Add methods for updating and deleting subreddits if needed.

class Threads:
    def __init__(self, connection):
        self.connection = connection

    def create_thread(self, subreddit_id, thread_title, thread_url, created_timestamp, upvotes, thread_author_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Threads (subreddit_id, thread_title, thread_url, created_timestamp, upvotes, thread_author_id) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING thread_id",
                (subreddit_id, thread_title, thread_url, created_timestamp, upvotes, thread_author_id)
            )
            self.connection.commit()
            return cursor.fetchone()[0]
        
    def get_threads_by_subreddit_id(self, subreddit_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT thread_id, subreddit_id, thread_title, thread_url, created_timestamp, upvotes, thread_author_id FROM Threads WHERE subreddit_id = %s",
                (subreddit_id,)
            )
            threads = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return threads
    
    def update_thread_sentiment_score(self, thread_id, sentiment_score):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE Threads SET thread_sentiment_score = %s WHERE thread_id = %s",
                (sentiment_score, thread_id)
            )
            self.connection.commit()

    def get_average_sentiment_score_by_subreddit_id(self, subreddit_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(thread_sentiment_score) AS average_sentiment_score
                FROM Threads
                WHERE subreddit_id = %s
                """,
                (subreddit_id,)
            )
            return cursor.fetchone()[0]

    # Add methods for reading, updating, and deleting threads if needed.

class Comments:
    def __init__(self, connection):
        self.connection = connection

    def create_comment(self, thread_id, comment_content, comment_author_id, created_timestamp, upvotes, depth, parent_comment_id, comment_score, comment_permalink):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Comments (thread_id, comment_content, comment_author_id, created_timestamp, upvotes, depth, parent_comment_id, comment_score, comment_permalink) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING comment_id",
                (thread_id, comment_content, comment_author_id, created_timestamp, upvotes, depth, parent_comment_id, comment_score, comment_permalink)
            )
            self.connection.commit()
            return cursor.fetchone()[0]
        
    def get_comments_by_thread_id(self, thread_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Comments WHERE thread_id = %s",
                (thread_id,)
            )
            comments = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return comments

    # Add methods for reading, updating, and deleting comments if needed.

class Users:
    def __init__(self, connection):
        self.connection = connection

    def create_user(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Users (username) VALUES (%s) RETURNING user_id",
                (username,)
            )
            self.connection.commit()
            return cursor.fetchone()[0]

    def get_user_by_username(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Users WHERE username = %s",
                (username,)
            )
            return cursor.fetchone()

    # Add methods for updating and deleting users if needed.

class SentimentScores:
    def __init__(self, connection):
        self.connection = connection

    def create_sentiment_score(self, comment_id, sentiment_score, sentiment_confidence):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO SentimentScores (comment_id, sentiment_score, sentiment_confidence) "
                "VALUES (%s, %s, %s)",
                (comment_id, sentiment_score, sentiment_confidence)
            )
            self.connection.commit()

    # Join the comment table with the sentiment score table by comment ID, and use the thread ID to get the average
    def get_average_sentiment_score_by_thread_id(self, thread_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(sentiment_score) AS average_sentiment_score
                FROM Comments
                JOIN SentimentScores ON Comments.comment_id = SentimentScores.comment_id
                WHERE Comments.thread_id = %s
                """,
                (thread_id,)
            )
            return cursor.fetchone()[0]

    # Add methods for reading, updating, and deleting sentiment scores if needed.


def is_valid_api_key(api_key):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * 
                FROM api_key 
                WHERE key = %s AND is_active = TRUE
                """,
                (api_key,)
            )
            rows = cur.fetchall()
            return len(rows)>0
    finally:
        connection_pool.putconn(conn)


