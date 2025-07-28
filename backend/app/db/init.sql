-- Initial SQL setup for Budul AI Islamic database
-- This file runs automatically when PostgreSQL container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "vector" CASCADE;

-- Create Islamic content-specific functions

-- Function to normalize Arabic text for search
CREATE OR REPLACE FUNCTION normalize_arabic_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Remove diacritics and normalize Arabic text
    RETURN regexp_replace(
        regexp_replace(
            regexp_replace(input_text, '[ًٌٍَُِّْ]', '', 'g'),  -- Remove diacritics
            '[أإآ]', 'ا', 'g'  -- Normalize Alif variants
        ),
        '[ةه]$', 'ه', 'g'  -- Normalize Ta Marbuta
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to extract root words from Arabic text (simplified)
CREATE OR REPLACE FUNCTION extract_arabic_roots(input_text TEXT)
RETURNS TEXT[] AS $$
DECLARE
    normalized_text TEXT;
    words TEXT[];
    word TEXT;
    roots TEXT[] := '{}';
BEGIN
    normalized_text := normalize_arabic_text(input_text);
    words := string_to_array(normalized_text, ' ');
    
    FOREACH word IN ARRAY words LOOP
        -- Simple root extraction (would use more sophisticated algorithm in production)
        IF length(word) >= 3 THEN
            roots := array_append(roots, substring(word from 1 for 3));
        END IF;
    END LOOP;
    
    RETURN roots;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to calculate content authenticity score
CREATE OR REPLACE FUNCTION calculate_authenticity_score(
    source_authority TEXT,
    authenticity_grade TEXT,
    scholar_consensus INTEGER DEFAULT 0
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN CASE
        WHEN authenticity_grade = 'sahih' AND source_authority = 'authentic' THEN 1.0
        WHEN authenticity_grade = 'sahih' THEN 0.95
        WHEN authenticity_grade = 'hasan' THEN 0.85
        WHEN authenticity_grade = 'daif' THEN 0.60
        WHEN source_authority = 'authentic' THEN 0.90  -- For Quran
        ELSE 0.50
    END + (scholar_consensus * 0.05);  -- Bonus for scholarly consensus
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Insert initial Islamic sources
INSERT INTO islamic_sources (id, name, source_type, authority_level, language, website_url, description) VALUES
(uuid_generate_v4(), 'Sahih Bukhari', 'hadith', 'sahih', 'ar', 'https://sunnah.com/bukhari', 'Most authentic hadith collection compiled by Imam Bukhari'),
(uuid_generate_v4(), 'Sahih Muslim', 'hadith', 'sahih', 'ar', 'https://sunnah.com/muslim', 'Second most authentic hadith collection compiled by Imam Muslim'),
(uuid_generate_v4(), 'Sunan Abu Dawud', 'hadith', 'hasan', 'ar', 'https://sunnah.com/abudawud', 'Collection of hadith compiled by Abu Dawud'),
(uuid_generate_v4(), 'Jami at-Tirmidhi', 'hadith', 'hasan', 'ar', 'https://sunnah.com/tirmidhi', 'Collection of hadith compiled by Imam Tirmidhi'),
(uuid_generate_v4(), 'Sunan an-Nasai', 'hadith', 'hasan', 'ar', 'https://sunnah.com/nasai', 'Collection of hadith compiled by Imam an-Nasai'),
(uuid_generate_v4(), 'Sunan Ibn Majah', 'hadith', 'hasan', 'ar', 'https://sunnah.com/ibnmajah', 'Collection of hadith compiled by Ibn Majah'),
(uuid_generate_v4(), 'Holy Quran', 'quran', 'authentic', 'ar', 'https://quran.com', 'The Holy Quran - direct word of Allah'),
(uuid_generate_v4(), 'Tafsir Ibn Kathir', 'tafsir', 'authentic', 'ar', 'https://quran.com/tafsir', 'Classical Quranic commentary by Ibn Kathir'),
(uuid_generate_v4(), 'Musnad Ahmad', 'hadith', 'hasan', 'ar', 'https://sunnah.com/ahmad', 'Large hadith collection by Imam Ahmad ibn Hanbal')
ON CONFLICT DO NOTHING;

-- Insert Islamic topic hierarchy
INSERT INTO islamic_topics (id, name, arabic_name, category_level, description) VALUES
-- Main categories (Level 1)
(uuid_generate_v4(), 'Aqeedah', 'عقيدة', 1, 'Islamic beliefs and creed'),
(uuid_generate_v4(), 'Fiqh', 'فقه', 1, 'Islamic jurisprudence and law'),
(uuid_generate_v4(), 'Seerah', 'سيرة', 1, 'Biography of Prophet Muhammad (PBUH)'),
(uuid_generate_v4(), 'Akhlaq', 'أخلاق', 1, 'Islamic ethics and morality'),
(uuid_generate_v4(), 'Ibadah', 'عبادة', 1, 'Acts of worship'),
(uuid_generate_v4(), 'Tafsir', 'تفسير', 1, 'Quranic interpretation'),
(uuid_generate_v4(), 'Hadith', 'حديث', 1, 'Prophetic traditions'),
(uuid_generate_v4(), 'History', 'تاريخ', 1, 'Islamic history')
ON CONFLICT DO NOTHING;

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_islamic_content_composite 
ON islamic_content(content_type, authenticity_grade, surah_number, verse_number);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_active 
ON chat_sessions(user_id, last_activity DESC) WHERE ended_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_api_usage_billing 
ON api_usage(user_id, created_at DESC, tokens_consumed);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;