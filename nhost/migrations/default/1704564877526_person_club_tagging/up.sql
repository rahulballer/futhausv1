CREATE TABLE person_club_tagging AS
SELECT a.*, b.short_name, b.total_tags, b.not_tags 
FROM sofascore a
LEFT JOIN club_tagging b ON a.club = b.club;
