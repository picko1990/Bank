import json
import os
from copy import copy

import requests
from django.conf import settings
from django.utils.log import AdminEmailHandler
# from django.views.debug import ExceptionReporter


class SlackExceptionHandler(AdminEmailHandler):

    # replacing default django emit (https://github.com/django/django/blob/master/django/utils/log.py)
    def emit(self, record, *args, **kwargs):

        # original AdminEmailHandler 'emit' method code (but without actually sending email)
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = record.getMessage()
            request = None
        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        data = {
            'payload': json.dumps({
                'text': f'*{record.levelname}:* {subject}',
                'unfurl_links': True}),
        }

        # setup channel webhook
        webhook_url = os.getenv('SLACK_WEBHOOK')

        # send it
        requests.post(webhook_url, data=data)
