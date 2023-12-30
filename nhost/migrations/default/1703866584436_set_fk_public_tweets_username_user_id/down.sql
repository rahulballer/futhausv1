alter table "public"."tweets" drop constraint "tweets_username_user_id_fkey",
  add constraint "tweets_user_id_username_fkey"
  foreign key ("user_id", "username")
  references "public"."consolidated_mastodon"
  ("user_id", "username") on update restrict on delete restrict;
