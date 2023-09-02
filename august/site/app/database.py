"""
Basic database class for the application.
This class will be used to interact with the database.
"""

import logging
import secrets
import sqlite3 as sql
import threading
import time

from webhook_logger import wh_logger

POSTS = []

with (
    open("posts/about_post.txt", "r") as about_post,
    open("posts/faq_post.txt", "r") as faq_post,
    open("posts/help_post.txt", "r") as help_post
):
    POSTS.append(("About Us", about_post.read(), "abffd306-2222-4e3c-899a-d71c9ffdc04a"))
    POSTS.append(("FAQ", faq_post.read(), "1c0614a9-1431-45d5-a273-ae5acd38b8ea"))
    POSTS.append(("Help", help_post.read(), "2a06cf39-714f-4375-b072-561c20c55749"))



class Database:
    def __init__(self):

        # Create a database in memory
        # We create one in memory because we don't really care about the data
        self.conn = sql.connect(":memory:", check_same_thread=False)

        # Initialize the database
        self.init_database()

    
    def init_database(self):

        print("Initializing database...")
        wh_logger.info("Initializing database...")

        # Create the tables
        cursor = self.conn.cursor()
        with open("init.sql", "r") as f:
            cursor.executescript(f.read())
        
        # Add optional code to add users into the database

        # Add admin
        cursor.execute(
            "INSERT INTO users (id, username, password, admin) VALUES (?, ?, ?, ?)",
            (123, "admin", "1ba144c30bf6ea67e0f01bc80acf423a203f3efc6cbf57299b44e11ae6456a4b", 1)
        )

        # Insert adminbot
        cursor.execute(
            "INSERT INTO users (id, username, password, admin) VALUES (?, ?, ?, ?)",
            (124, "adminbot", "7ec72afcace768de7741427c287523638d8d839812274ebcb0f1246e39bbc89e", 1)
        )

        for post in POSTS:
            cursor.execute(
                "INSERT INTO posts (user_id, title, content, link, approved, seen) VALUES (?, ?, ?, ?, ?, ?)",
                (123, post[0], post[1], post[2], 1, 1)
            )

        # Commit the changes
        self.conn.commit()

        cursor.close()
        print("Database initialized.")
        wh_logger.info("Database initialized.")

        self.JWT_KEY = secrets.token_urlsafe(32)
        print(f"New JWT key generated: {self.JWT_KEY}")


    def get_user_id(self, username) -> int | bool:
        """
        Get a user's id from the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            )
            user = cursor.fetchone()
            cursor.close()
            if user:
                return user[0]
            else:
                return False
        except Exception as e:
            logging.error(e)
            return False
        

    def is_admin(self, user_id) -> bool:
        """
        Check if a user is an admin.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT admin FROM users WHERE id = ?", (user_id,)
            )
            admin = cursor.fetchone()
            cursor.close()
            logging.info(admin)
            if admin and admin[0] == 1:
                return True
            else:
                return False
        except Exception as e:
            logging.error(e)
            return False
        

    def add_user(self, username, password) -> bool:
        """
        Add a user to the database.

        Usually the password should be hashed, but for this example we will
        just store it in plain text.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(e)
            return False
        

    def login(self, username, password) -> int | bool:
        """
        Check if a user's credentials are valid.
        If it is, return the user's id.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password = ?", (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            if user:
                return user[0]
            else:
                return False
        except Exception as e:
            logging.error(e)
            return False
        

    def get_all_users(self):
        """
        Debug function to get all users in the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM users"
            )
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as e:
            logging.error(e)
            return False
        

    def get_post_by_user(self, user_id) -> list[tuple[str, str, str, int, int]] | bool:
        """
        Get all posts by a user.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT title, content, link, user_id, approved FROM posts WHERE user_id = ?", (user_id,)
            )
            posts = cursor.fetchall()
            cursor.close()
            return posts
        except Exception as e:
            logging.error(e)
            return False
        

    def get_post_by_link(self, link) -> list[tuple[str, str, str, int, int]] | bool:
        """
        Get a post by its link.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT title, content, link, user_id, approved FROM posts WHERE link = ?", (link,)
            )
            post = cursor.fetchone()
            cursor.close()
            return post
        except Exception as e:
            logging.error(e)
            return False
        

    def add_post(self, title, content, link, user_id) -> bool:
        """
        Add a post to the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO posts (user_id, title, content, link) VALUES (?, ?, ?, ?)", (user_id, title, content, link)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(e)
            return False
        

    def delete_post(self, link) -> bool:
        """
        Delete a post from the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM posts WHERE link = ?", (link,)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(e)
            return False
        

    def get_all_posts(self) -> list[tuple[int, str, str, str, int, int, int]] | bool:
        """
        Get all posts in the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM posts"
            )
            posts = cursor.fetchall()
            cursor.close()
            return posts
        except Exception as e:
            logging.error(e)
            return False
        
    
    def get_all_unseen_posts_links(self) -> list[tuple[str]] | bool:
        """
        Get all unseen posts in the database.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT link FROM posts WHERE seen = 0"
            )
            posts = cursor.fetchall()
            cursor.close()
            return posts
        except Exception as e:
            logging.error(e)
            return False
        
    
    def mark_post_as_seen(self, link) -> bool:
        """
        Mark a post as seen.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE posts SET seen = 1 WHERE link = ?", (link,)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logging.error(e)
            return False
        

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
        print("Database connection closed.")
        wh_logger.info("Database connection closed.")


    def restart(self):
        """
        Restart the database.
        """
        print("Restarting database...")
        wh_logger.info("Restarting database...")
        self.init_database()
        print("Database restarted.")
        wh_logger.info("Database restarted.")


database = Database()


# Setup a loop to reset the database every hour
def reset_db():
    while True:
        time.sleep(60 * 60)
        database.restart()

restart_db_thread = threading.Thread(target=reset_db, daemon=True)
