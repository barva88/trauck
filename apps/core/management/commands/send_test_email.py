from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send a test email using current EMAIL_BACKEND and SMTP settings'

    def add_arguments(self, parser):
        parser.add_argument('--to', help='Recipient email', default=None)

    def handle(self, *args, **options):
        to = options.get('to') or ''
        if not to:
            self.stdout.write('No recipient provided with --to; use EMAIL_HOST_USER as recipient for quick test')
            from django.conf import settings
            to = settings.EMAIL_HOST_USER or ''
            if not to:
                self.stderr.write('No recipient and no EMAIL_HOST_USER configured; aborting')
                return
        try:
            send_mail('Trauck test email', 'This is a test email from Trauck.', None, [to])
            self.stdout.write(self.style.SUCCESS(f'Test email sent to {to} (check inbox/spam).'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to send test email: {e}'))
