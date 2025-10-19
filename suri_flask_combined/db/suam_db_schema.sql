-- 📘 Suri 명리 SQLite 스키마 (suam_db_schema.sql)

PRAGMA foreign_keys = ON;

CREATE TABLE forces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    elements TEXT,
    traits TEXT,
    interpretation TEXT
);

CREATE TABLE ten_gods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    relation TEXT,
    category TEXT,
    description TEXT
);

CREATE TABLE geokuk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    condition TEXT,
    explanation TEXT,
    job_field TEXT
);

CREATE TABLE shinsal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    meaning TEXT,
    trigger TEXT
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    elements TEXT,
    effect TEXT,
    description TEXT
);

CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger TEXT,
    outcome TEXT,
    category TEXT
);

CREATE TABLE exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    rule TEXT
);

CREATE TABLE ai_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_saju TEXT,
    output_text TEXT,
    tags TEXT
);
