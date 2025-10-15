-- 📘 규칙 테이블
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    content TEXT,
    keywords TEXT,
    example TEXT,
    source TEXT
);

-- 📙 용어 테이블
CREATE TABLE IF NOT EXISTS terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT,
    definition TEXT,
    category TEXT,
    source TEXT
);

-- 📗 사례 테이블
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    chart TEXT,
    summary TEXT,
    content TEXT,
    tags TEXT,
    source TEXT
);

-- 📎 규칙 ↔ 사례 관계 테이블
CREATE TABLE IF NOT EXISTS case_rule_link (
    case_id INTEGER,
    rule_id INTEGER,
    FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY(rule_id) REFERENCES rules(id) ON DELETE CASCADE
);

-- 📎 용어 ↔ 사례 관계 테이블
CREATE TABLE IF NOT EXISTS case_term_link (
    case_id INTEGER,
    term_id INTEGER,
    FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
    FOREIGN KEY(term_id) REFERENCES terms(id) ON DELETE CASCADE
);

-- 🔍 검색 성능 향상을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category);
CREATE INDEX IF NOT EXISTS idx_cases_tags ON cases(tags);
CREATE INDEX IF NOT EXISTS idx_terms_category ON terms(category);
CREATE INDEX IF NOT EXISTS idx_case_rule ON case_rule_link(case_id, rule_id);
CREATE INDEX IF NOT EXISTS idx_case_term ON case_term_link(case_id, term_id);
