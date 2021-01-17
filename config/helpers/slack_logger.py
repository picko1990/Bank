import json
import os
import time
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
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        # if record.exc_info:
        #     exc_info = record.exc_info
        # else:
        #     exc_info = (None, record.getMessage(), None)

        # reporter = ExceptionReporter(request, is_email=True, *exc_info)
        # message = reporter.get_traceback_data()
        # message = '%s\n\n%s' % (self.format(no_exc_record), reporter.get_traceback_text())

        # self.send_mail(subject, message, fail_silently=True, html_message=html_message)

        # this is where original 'emit' method code ends

        # construct slack attachment detail fields
        # colors = {
        #     'ERROR': 'danger',
        #     'INFO': 'good',
        #     'WARNING': 'warning'
        # }
        # attachments = [
        #     {
        #         'title': subject,
        #         'color': colors.get(record.levelname, '#1d9bd1'),
        #         'fields': [
        #             {
        #                 'title': 'Level',
        #                 'value': record.levelname,
        #                 'short': True,
        #             },
        #             {
        #                 'title': 'Method',
        #                 'value': request.method if request else 'No Request',
        #                 'short': True,
        #             },
        #             {
        #                 'title': 'Path',
        #                 'value': request.path if request else 'No Request',
        #                 'short': True,
        #             },
        #             {
        #                 'title': 'User',
        #                 'value': ((request.user.username + ' (' + str(request.user.pk) + ')'
        #                            if request.user.is_authenticated else 'Anonymous')
        #                           if request else 'No Request'),
        #                 'short': True,
        #             },
        #             {
        #                 'title': 'Status Code',
        #                 'value': getattr(record, 'status_code', None),
        #                 'short': True,
        #             },
        #             {
        #                 'title': 'UA',
        #                 'value': (request.META['HTTP_USER_AGENT']
        #                           if request and request.META else 'No Request'),
        #                 'short': False,
        #             },
        #             {
        #                 'title': 'GET Params',
        #                 'value': json.dumps(request.GET) if request else 'No Request',
        #                 'short': False,
        #             }
        #         ],
            },

        ]
        # if record.levelname == 'ERROR':
        #     extra_data = [
        #         'frames',
        #         'request_meta',
        #         'filtered_POST_items',
        #         'template_info',
        #         'template_does_not_exist',
        #         'postmortem'
        #     ]

        #     slack message attachment text has max of 8000 bytes
        #     lets split it up into 7900 bytes long chunks to be on the safe side
        #     split = 7900
        #     byte_size = 0
        #     response = ''
        #     part = 1

        #     for field in extra_data:
        #         data = json.dumps(message[field], indent=2, default=str)
        #         byte_size += len(data) + len(field) + len(data) + 3
        #         if byte_size < split:
        #             response += f'{field}:\n{data}\n'
        #         else:
        #             # add main error message body
        #             attachments.append({
        #                 'color': 'danger',
        #                 'title': f'Extra details ({part})',
        #                 'text': response,
        #                 'ts': time.time(),
        #             })

        #             part += 1
        #             byte_size = len(data) + len(field) + len(data) + 3
        #             response = f'{field}:\n{data}\n'
        #     # add main error message body
        #     attachments.append({
        #         'color': 'danger',
        #         'title': f'Extra details ({part})',
        #         'text': response,
        #         'ts': time.time(),
        #     })

        # construct main text
        # main_text = 'Alert at ' + time.strftime('%A, %d %b %Y %H:%M:%S +0000', time.gmtime())

        # construct data
        data = {
            'payload': json.dumps({
                'text': f'*{record.levelname}:* {subject}',
                'unfurl_links': True}),
        }

        # setup channel webhook
        webhook_url = os.getenv('SLACK_WEBHOOK')

        # send it
        requests.post(webhook_url, data=data)
