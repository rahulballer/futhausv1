alter table "public"."tweets" alter column "content_cleaned_for_tagging" drop not null;
alter table "public"."tweets" add column "content_cleaned_for_tagging" text;
