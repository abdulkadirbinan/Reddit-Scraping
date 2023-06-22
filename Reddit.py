import praw
import mysql.connector
from flask import Flask, jsonify
import threading
import datetime
print("Welcome!Please enter a subreddit name.")
subbredditname = input()

client_id = "<your_client_id>"
client_secret = "<your_client_secre>"
username = "<your_username>"
password = "<your_password>"
db = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="", 
    database="redditscraping"
)
app = Flask(__name__)


reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent="abdulkadirbinan",
)

cursor = db.cursor(buffered=True)

create_table_query = """
CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id VARCHAR(255),
    title VARCHAR(255),
    content VARCHAR(255),
    author VARCHAR(255),
    url VARCHAR(255),
    image_url VARCHAR(255),
    video_url VARCHAR(255),
    created_utc TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
cursor.execute(create_table_query)
db.commit()
def fetch_posts():
    subreddit = reddit.subreddit("Subreddit Name:" + subbredditname)
    for submission in subreddit.new(limit=10):
        
        post_id = submission.id
        cursor.execute("SELECT * FROM posts WHERE post_id = %s", (post_id,))
        result = cursor.fetchone()

        if not result:
            post_title = submission.title
            post_content = submission.selftext
            post_author = submission.author.name
            post_url = submission.url
            image_url = None
            video_url = None
            created_utc = datetime.datetime.utcfromtimestamp(submission.created_utc)
            if submission.is_self:
                post_url = submission.url
            else:
    
                if submission.url.endswith((".jpg", ".jpeg", ".png")):
                    image_url = submission.url
                elif submission.is_video:
                    video_url = submission.media["reddit_video"]["fallback_url"]
                post_url = f"https://www.reddit.com{submission.permalink}"

            insert_query = "INSERT INTO posts (post_id, title, content, author, url, image_url, video_url, created_utc) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
            post_data = (
                post_id,
                post_title,
                post_content,
                post_author,
                post_url,
                image_url,
                video_url,
                created_utc,
            )
            cursor.execute(insert_query, post_data)
            db.commit()
    
    
    threading.Timer(60, fetch_posts).start()

@app.route("/posts", methods=["GET"])
def get_posts():
    cursor = db.cursor(buffered=True)
    query = "SELECT * FROM posts"
    cursor.execute(query)
    result = cursor.fetchall()
    posts = []

    for row in result:
        post = {
            "id": row[0],
            "post_id": row[1],
            "title": row[2],
            "content": row[3],
            "author": row[4],
            "url": row[5],
            "image_url": row[6],
            "video_url": row[7],
            "created_utc": row[8].isoformat(),
        }
        posts.append(post)
    cursor.close()
    return jsonify(posts)

if __name__ == "__main__":
    fetch_posts()
    app.run(debug=True, use_reloader=False)
