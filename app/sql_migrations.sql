-- =========================================================
-- MIGRATION: Intelligent Search — FULLTEXT Indexes
-- Project: CapIQ Replacement (Coresight Research)
-- Date: 2026-02-24
-- 
-- INSTRUCTIONS: Run these queries on BOTH dev and production
-- databases. These are one-time DDL changes.
-- =========================================================

-- ---------------------------------------------------------
-- 1. FULLTEXT index on News Articles (title + summary)
--    Table: coreiq_av_market_news_sentiment
--    Purpose: Enable MATCH AGAINST for relevance-ranked
--            keyword search on news headlines and summaries
-- ---------------------------------------------------------
ALTER TABLE coreiq_av_market_news_sentiment 
ADD FULLTEXT INDEX idx_news_fulltext_search (title, summary);

-- ---------------------------------------------------------
-- 2. FULLTEXT index on Earnings Call Transcripts
--    Table: coreiq_av_earnings_call_transcripts
--    Purpose: Enable MATCH AGAINST for transcript search
--            (used as fallback; primary search is TF-IDF)
-- ---------------------------------------------------------
ALTER TABLE coreiq_av_earnings_call_transcripts 
ADD FULLTEXT INDEX idx_transcript_fulltext_search (transcript_text);

-- =========================================================
-- VERIFICATION: Run after migration to confirm indexes exist
-- =========================================================
SHOW INDEX FROM coreiq_av_market_news_sentiment WHERE Key_name = 'idx_news_fulltext_search';
SHOW INDEX FROM coreiq_av_earnings_call_transcripts WHERE Key_name = 'idx_transcript_fulltext_search';
