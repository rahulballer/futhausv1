alter table "public"."tweets" add column "source" text
 not null default 'Twitter';
