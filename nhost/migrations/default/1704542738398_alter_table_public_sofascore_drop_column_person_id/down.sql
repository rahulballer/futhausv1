alter table "public"."sofascore" alter column "person_id" drop not null;
alter table "public"."sofascore" add column "person_id" text;
