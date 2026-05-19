-- ─────────────────────────────────────────────────────
--  Sport Events – MySQL setup script
--  Run once:  mysql -u root -p < setup_db.sql
-- ─────────────────────────────────────────────────────

CREATE DATABASE IF NOT EXISTS sport_events
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sport_events;

-- Tables are created automatically by SQLAlchemy (models.py)
-- This file only exists to create the database itself.

-- Optionally create a dedicated application user:
-- CREATE USER IF NOT EXISTS 'sport_user'@'localhost' IDENTIFIED BY 'strong_password';
-- GRANT ALL PRIVILEGES ON sport_events.* TO 'sport_user'@'localhost';
-- FLUSH PRIVILEGES;

SELECT 'Database sport_events ready ✓' AS status;
