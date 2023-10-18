-- Create the Subreddits table
CREATE TABLE Subreddits (
    subreddit_id SERIAL PRIMARY KEY,
    subreddit_name VARCHAR(255) NOT NULL,
    subreddit_description VARCHAR(255),
    subreddit_url VARCHAR(255),
    subreddit_sentiment_score INT
);

-- Create the Users table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL
    -- Add other user-specific columns as needed
);

-- Create the Threads table
CREATE TABLE Threads (
    thread_id SERIAL PRIMARY KEY,
    subreddit_id INT REFERENCES Subreddits(subreddit_id),
    thread_title VARCHAR(255) NOT NULL,
    thread_url VARCHAR(255),
    created_timestamp TIMESTAMP,
    upvotes INT,
    thread_sentiment_score INT,
    thread_author_id INT REFERENCES Users(user_id)
);

-- Create the Comments table
CREATE TABLE Comments (
    comment_id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES Threads(thread_id),
    comment_content TEXT NOT NULL,
    comment_author_id INT REFERENCES Users(user_id),
    created_timestamp TIMESTAMP,
    upvotes INT,
    depth INT,
    parent_comment_id INT,
    comment_sentiment_score INT,
    comment_permalink VARCHAR(255)
);

-- Create the Sentiment Scores table
CREATE TABLE SentimentScores (
    comment_id INT,
    sentiment_score NUMERIC,
    sentiment_subjectivity NUMERIC
);

