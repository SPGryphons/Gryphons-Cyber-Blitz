-- This is the first file that is executed when the database is created.

-- Remove the table if it exists
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

-- Create the table
CREATE TABLE users(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  admin BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE posts(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  link VARCHAR(255) NOT NULL,
  user_id INTEGER NOT NULL,
  approved BOOLEAN NOT NULL DEFAULT 0,
  seen BOOLEAN NOT NULL DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(id)
);