-- For each table:
-- * Rename 'create' columns
-- * Add new 'create' columns
-- * Add migrations table?
-- * !!! Semicolon after each alter !!!

-- ALTER TABLE <table_name> RENAME COLUMN <column_name> TO <new_column_name>;

-- comments
ALTER TABLE submissions CREATE COLUMN self_promo_check NOT NULL BOOLEAN default FALSE;
