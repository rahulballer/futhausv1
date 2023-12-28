alter table "public"."consolidated_mastodon" add column "source" text
 not null default 'twitter';
