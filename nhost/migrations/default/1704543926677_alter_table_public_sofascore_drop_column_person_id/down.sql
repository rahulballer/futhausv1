alter table "public"."sofascore" add constraint "sofascore_person_id_key" unique (person_id);
alter table "public"."sofascore" alter column "person_id" drop not null;
alter table "public"."sofascore" add column "person_id" int4;
