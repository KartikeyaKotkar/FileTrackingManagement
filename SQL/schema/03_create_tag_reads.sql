CREATE TABLE IF NOT EXISTS tag_reads (
    id          SERIAL PRIMARY KEY,
    epc         TEXT NOT NULL,
    reader_name TEXT NOT NULL,
    antenna     INTEGER NOT NULL,
    timestamp   TIMESTAMPTZ NOT NULL,
    rssi        INTEGER NOT NULL,
    location    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tag_reads_epc ON tag_reads (epc);
