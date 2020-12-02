from django.core.management.base import BaseCommand, CommandError
from django.db import connection

class Command(BaseCommand):
    help = 'Alter fast_feature table in the database so the query planner is efficient'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(
            """
            ALTER TABLE layers_fastfeaturestatus SET(
            autovacuum_enabled=true,
            autovacuum_vacuum_threshold=50,
            autovacuum_vacuum_scale_factor=0.2,
            autovacuum_analyze_threshold=1,
            autovacuum_vacuum_cost_delay=20,
            autovacuum_vacuum_cost_limit=200,
            autovacuum_freeze_min_age=50000000,
            autovacuum_freeze_max_age=200000000,
            autovacuum_freeze_table_age=150000000
            );
            """)
        cursor.close()
        print "Alter table complete"
