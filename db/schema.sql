-- DVDPA schema. ISSUE 5 (schema_sql): personal-data columns declared with no
-- field-level protection and no retention rule. Each one is an inventory entry
-- the data map needs. S.4, S.5, S.8(7), S.8(5), Rule 6(1)(a). The dob column
-- also engages S.9 (children).
CREATE TABLE IF NOT EXISTS customers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    aadhaar_no    CHAR(12),
    pan_no        CHAR(10),
    mobile        VARCHAR(16),
    email         TEXT,
    upi_id        TEXT,
    dob           DATE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kyc_documents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER REFERENCES customers(id),
    passport_no   VARCHAR(9),
    voter_id      VARCHAR(10),
    dl_no         VARCHAR(20),
    selfie_path   TEXT,
    uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A table that is NOT about people: its `name` column must not be reported.
CREATE TABLE IF NOT EXISTS plans (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    price_paise   INTEGER NOT NULL
);
