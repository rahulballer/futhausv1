alter table "public"."tweets"
  add constraint "tweets_username_user_id_fkey"
  foreign key ("username", "user_id")
  references "public"."consolidated_mastodon"
  ("username", "user_id") on update set null on delete set null;
