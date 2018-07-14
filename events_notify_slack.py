import json
import logging
import os

from urllib2 import Request, urlopen

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
HOOK_URL = os.environ['HOOK_URL']


def lambda_handler(event, context):
    """
    Handle the lambda call

    :param dict event: Event data
    :param context: Lambda function context
    """
    logger.info("Event: %s", event)
    region = event['region']
    resources = event['resources']
    detail = event['detail']
    service = detail['service']
    color = 'danger'
    msg = json.dumps(build_message(event, color))

    # Generate the request
    if not msg:
        logger.error('Message building failed.')
        return

    request = Request(HOOK_URL, msg)

    try:
        # Perform request
        response = urlopen(request)
        logger.info("Message posted to Slack: %s", msg)
        data = response.read()
        logger.info("Response: %s", data)
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


def build_message(data, color=''):
    """
    Build a message for Slack

    :param dict data: Message data
    :param str color: Attachment color
    :return: Slack message dict
    :rtype: dict
    """
    message = {
        'attachments': []
    }

    fields = [
        {
            'title': 'Region',
            'value': data['region'],
            'short': True
        },
        {
            'title': 'Service',
            'value': data['detail']['service'],
            'short': True
        }
    ]

    # Resources
    if data['resources']:
        fields.append({
            'title': 'Resources',
            'value': ', '.join(data['resources']),
            'short': False
        })

    # Title link
    title_link = build_title_link(data['detail']['eventArn'])

    # Text
    text = ''
    for item in data['detail']['eventDescription']:
        text = item['latestDescription'] + '\n' + text

    # Build the attachment and append it to the message
    attachment = {
        'fallback': data['detail']['eventTypeCode'],
        'color': color,
        'title': data['detail']['eventTypeCode'],
        'title_link': title_link,
        'text': text,
        'fields': fields,
        'footer': 'CloudWatch Event'
    }
    message['attachments'].append(attachment)
    return message


def build_title_link(arn):
    """
    Build link to personal health dashboard to view the event

    :param str arn: Event ARN
    """
    return "https://phd.aws.amazon.com/phd/home#/event-log?eventID=%s&eventTab=details&layout=vertical" % arn
