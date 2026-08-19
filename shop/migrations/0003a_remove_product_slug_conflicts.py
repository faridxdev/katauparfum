from django.db import migrations


SQL = '''
DO $$
DECLARE r record;
BEGIN
  -- Drop any constraints named like 'shop_product_slug%'
  FOR r IN SELECT conname FROM pg_constraint
           WHERE conrelid = 'public.shop_product'::regclass AND conname LIKE 'shop_product_slug%'
  LOOP
    EXECUTE format('ALTER TABLE public.shop_product DROP CONSTRAINT IF EXISTS %I', r.conname);
  END LOOP;

  -- Drop any indexes on public.shop_product whose name matches 'shop_product_slug%'
  FOR r IN SELECT indexname FROM pg_indexes
           WHERE schemaname='public' AND tablename='shop_product' AND indexname LIKE 'shop_product_slug%'
  LOOP
    EXECUTE format('DROP INDEX IF EXISTS public.%I', r.indexname);
  END LOOP;
END$$;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_review'),
    ]

    operations = [
        migrations.RunSQL(SQL, reverse_sql=migrations.RunSQL.noop),
    ]
