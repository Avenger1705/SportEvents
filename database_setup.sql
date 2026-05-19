-- ═══════════════════════════════════════════════════════════════════════════
--  SportEventsWeb — Complete Database Setup
--  Run once:  mysql -u root -p < database_setup.sql
--  This file creates the database AND all tables.
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 1. Create database ────────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS sport_events
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sport_events;

-- ── 2. Users ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    nom                 VARCHAR(100)  NULL,
    prenom              VARCHAR(100)  NULL,
    address             VARCHAR(255)  NULL,
    username            VARCHAR(50)   NOT NULL UNIQUE,
    email               VARCHAR(100)  NOT NULL UNIQUE,
    password_hash       VARCHAR(255)  NOT NULL,
    role                ENUM('admin','joueur','visitor') NULL,
    is_verified         BOOLEAN       NOT NULL DEFAULT FALSE,
    otp_code            VARCHAR(6)    NULL,
    otp_expires_at      DATETIME      NULL,
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Athlete / player fields
    age                 INT           NULL,
    height              FLOAT         NULL,
    weight              FLOAT         NULL,
    ranking             VARCHAR(50)   NULL,
    mean_global_ranking VARCHAR(50)   NULL,
    profile_image       VARCHAR(255)  NULL,
    practice_sport      VARCHAR(100)  NULL,
    matches_played      INT           NOT NULL DEFAULT 0,
    matches_won         INT           NOT NULL DEFAULT 0,
    matches_lost        INT           NOT NULL DEFAULT 0,
    INDEX idx_username  (username),
    INDEX idx_email     (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 3. Athlete preferences ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS athlete_preferences (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL UNIQUE,
    practice_sport VARCHAR(100) NOT NULL,
    CONSTRAINT fk_ap_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 4. Sport interests ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sport_interests (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL,
    sport_name     VARCHAR(100) NOT NULL,
    interest_level SMALLINT     NOT NULL DEFAULT 3,
    notify         BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_si_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 5. Visitor preferences ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS visitor_preferences (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT  NOT NULL UNIQUE,
    favorite_sports TEXT NULL,
    CONSTRAINT fk_vp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 6. Events ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    description  TEXT         NULL,
    sport        VARCHAR(100) NULL,
    location     VARCHAR(200) NULL,
    latitude     FLOAT        NULL,
    longitude    FLOAT        NULL,
    cover_photo  VARCHAR(255) NULL,
    event_date   DATETIME     NULL,
    event_time   VARCHAR(50)  NULL,
    duration     VARCHAR(50)  NULL,
    organizer_id INT          NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ev_organizer FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 7. Event photos ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS event_photos (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    event_id   INT          NOT NULL,
    photo_path VARCHAR(255) NOT NULL,
    CONSTRAINT fk_ep_event FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 8. Comments (on events) ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    event_id   INT      NOT NULL,
    user_id    INT      NOT NULL,
    content    TEXT     NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_co_event FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    CONSTRAINT fk_co_user  FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 9. Teams ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    sport      VARCHAR(100) NOT NULL,
    logo       VARCHAR(255) NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INT          NULL,
    CONSTRAINT fk_te_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 10. Team members ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS team_members (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    team_id       INT          NOT NULL,
    user_id       INT          NULL,
    player_name   VARCHAR(100) NOT NULL,
    player_email  VARCHAR(100) NULL,
    position      VARCHAR(50)  NULL,
    jersey_number INT          NULL,
    CONSTRAINT fk_tm_team FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    CONSTRAINT fk_tm_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 11. Tournaments ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tournaments (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(200) NOT NULL,
    sport          VARCHAR(100) NOT NULL,
    description    TEXT         NULL,
    location       VARCHAR(200) NULL,
    start_date     DATETIME     NULL,
    end_date       DATETIME     NULL,
    match_duration VARCHAR(50)  NULL,
    status         VARCHAR(20)  NOT NULL DEFAULT 'a_venir',
    cover_photo    VARCHAR(255) NULL,
    created_by     INT          NULL,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_to_creator FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 12. Tournament teams ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tournament_teams (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT  NOT NULL,
    team_id       INT  NOT NULL,
    seed          INT  NULL,
    CONSTRAINT fk_tt_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    CONSTRAINT fk_tt_team       FOREIGN KEY (team_id)       REFERENCES teams(id)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 13. Matches ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS matches (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT          NOT NULL,
    round_number  INT          NOT NULL,
    match_order   INT          NOT NULL,
    team_a_id     INT          NULL,
    team_b_id     INT          NULL,
    score_a       INT          NULL,
    score_b       INT          NULL,
    winner_id     INT          NULL,
    match_date    DATETIME     NULL,
    match_time    VARCHAR(50)  NULL,
    location      VARCHAR(200) NULL,
    status        ENUM('a_venir','en_cours','termine','reporte') NOT NULL DEFAULT 'a_venir',
    played_at     DATETIME     NULL,
    CONSTRAINT fk_ma_tournament FOREIGN KEY (tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
    CONSTRAINT fk_ma_team_a     FOREIGN KEY (team_a_id)     REFERENCES teams(id) ON DELETE SET NULL,
    CONSTRAINT fk_ma_team_b     FOREIGN KEY (team_b_id)     REFERENCES teams(id) ON DELETE SET NULL,
    CONSTRAINT fk_ma_winner     FOREIGN KEY (winner_id)     REFERENCES teams(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 14. Bookings ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT          NOT NULL,
    match_id  INT          NOT NULL,
    qr_code   VARCHAR(255) NULL,
    booked_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bo_user  FOREIGN KEY (user_id)  REFERENCES users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_bo_match FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── 15. Match comments ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS match_comments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    match_id   INT      NOT NULL,
    user_id    INT      NOT NULL,
    content    TEXT     NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mc_match FOREIGN KEY (match_id) REFERENCES matches(id)  ON DELETE CASCADE,
    CONSTRAINT fk_mc_user  FOREIGN KEY (user_id)  REFERENCES users(id)    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Done ──────────────────────────────────────────────────────────────────
SELECT 'SportEventsWeb database ready ✓' AS status;
