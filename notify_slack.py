import json
import logging
import os

from slacker import Slacker

from events.health import HealthEvent
from events.sns import SNSEvent

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
SLACK_TOKEN = os.environ['SLACK_TOKEN']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']


def lambda_handler(event, context):
    """
    Handle the lambda call

    :param dict event: Event data
    :param context: Lambda function context
    """
    message = None

    # Log the incoming event
    logger.info("Received event", event)

    # Check if the event has records
    if 'Records' in event:
        # Look at the first record to see what kind of event it is
        record = event['Records'][0]

        if record['EventSource'] == 'aws:sns':
            notification = SNSEvent(event)
            message = notification.build_message()
    elif 'source' in event:
        # This may be a CloudWatch event
        if event['source'] == 'aws.health':
            notification = HealthEvent(event)
            message = notification.build_message()

    if message:
        print(json.dumps(message.build()))
        slacker = Slacker(token=SLACK_TOKEN)
        slacker.chat.post_message(
            channel=SLACK_CHANNEL,
            attachments=message.attachments
        )
    else:
        logger.error('Message was not generated')
