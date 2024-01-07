BEGIN TRANSACTION;
ALTER TABLE "public"."sofascore" DROP CONSTRAINT "sofascore_pkey";

ALTER TABLE "public"."sofascore"
    ADD CONSTRAINT "sofascore_pkey" PRIMARY KEY ("id");
COMMIT TRANSACTION;
