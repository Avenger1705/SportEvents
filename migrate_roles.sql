-- ─────────────────────────────────────────────────────
--  Sport Events – MySQL Migration Script
--  Adds nom, prenom, address columns + updates role enum
--  Run:  mysql -u root -p sport_events < migrate_roles.sql
-- ─────────────────────────────────────────────────────

USE sport_events;

-- 1. Add new columns if they don't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS nom     VARCHAR(100) NULL AFTER id;
ALTER TABLE users ADD COLUMN IF NOT EXISTS prenom  VARCHAR(100) NULL AFTER nom;
ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR(255) NULL AFTER prenom;

-- 2. Update the role enum to new values: admin, joueur, visitor
ALTER TABLE users MODIFY COLUMN role ENUM('admin','joueur','visitor') NULL;

-- 3. Migrate old role values to new ones
UPDATE users SET role = 'joueur'  WHERE role = 'athlete';
UPDATE users SET role = 'admin'   WHERE role = 'organizer';

SELECT 'Migration complete ✓' AS status;
