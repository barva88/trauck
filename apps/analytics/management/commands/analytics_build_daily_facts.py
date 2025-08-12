from datetime import datetime, date
from django.core.management.base import BaseCommand
from apps.analytics.services.aggregates import build_range

class Command(BaseCommand):
    help = 'Build analytics daily fact tables over a date range'

    def add_arguments(self, parser):
        parser.add_argument('--from', dest='from_date', required=False, help='YYYY-MM-DD')
        parser.add_argument('--to', dest='to_date', required=False, help='YYYY-MM-DD')

    def handle(self, *args, **opts):
        to_dt = datetime.strptime(opts['to_date'], '%Y-%m-%d').date() if opts.get('to_date') else date.today()
        from_dt = datetime.strptime(opts['from_date'], '%Y-%m-%d').date() if opts.get('from_date') else to_dt
        build_range(from_dt, to_dt)
        self.stdout.write(self.style.SUCCESS(f'Built facts from {from_dt} to {to_dt}'))
