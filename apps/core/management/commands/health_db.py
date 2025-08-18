from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Checks database connectivity by running SELECT 1"

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                if row and row[0] == 1:
                    self.stdout.write(self.style.SUCCESS("DB OK"))
                    return 0
                else:
                    self.stdout.write(self.style.ERROR("DB NOT OK"))
                    return 1
        except Exception as ex:
            self.stderr.write(self.style.ERROR(f"DB ERROR: {ex}"))
            return 1
