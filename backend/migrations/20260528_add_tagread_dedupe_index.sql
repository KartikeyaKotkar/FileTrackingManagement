CREATE INDEX IF NOT EXISTS idx_tagread_dedupe
ON tag_reads (epc, reader_name, antenna, timestamp);
