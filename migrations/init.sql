-- migrations/init.sql
CREATE TABLE IF NOT EXISTS comments (
  id SERIAL PRIMARY KEY,
  target TEXT NOT NULL,         -- "A" | "B" | "C"
  comment_text TEXT NOT NULL,
  from_user_id BIGINT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  is_blocked BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY,         -- Telegram user_id
  blocked BOOLEAN DEFAULT false,
  last_comment_at TIMESTAMP WITH TIME ZONE
);
