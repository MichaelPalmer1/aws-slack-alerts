import json
import logging

from events.sns import SNSEvent

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
# HOOK_URL = os.environ['HOOK_URL']


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

        if 'Sns' in record:
            notification = SNSEvent(event)
            message = notification.build_message()

    if message:
        print(json.dumps(message))
    else:
        logger.error('Message was not generated')
