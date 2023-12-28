alter table "public"."tweets" alter column "source" set default ''Twitter'::text';
alter table "public"."tweets" alter column "source" drop not null;
alter table "public"."tweets" add column "source" text;
