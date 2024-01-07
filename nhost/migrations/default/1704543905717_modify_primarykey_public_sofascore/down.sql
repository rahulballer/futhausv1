alter table "public"."sofascore" drop constraint "sofascore_pkey";
alter table "public"."sofascore"
    add constraint "sofascore_pkey"
    primary key ("person_id");
