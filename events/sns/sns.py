import json

from slack import SlackMessage, SlackAttachment
from events.base import Event


class SNSEvent(Event):

    def __init__(self, event):
        super(SNSEvent, self).__init__(event)
        self.sns = self.event['Records'][0]['Sns']
        self.subject = self.sns['Subject']
        self.topic = self.sns['TopicArn']
        self.message = json.loads(self.sns['Message'])
        topic_parts = self.topic.split(':')
        self.account_id = topic_parts[4]
        self.region = topic_parts[3]

    def build_message(self):
        event_class = None

        if 'AutoScalingGroupARN' in self.message:
            from events.sns.autoscaling import AutoScalingEvent
            event_class = AutoScalingEvent

        elif 'AlarmName' in self.message:
            from events.sns.alarm import AlarmEvent
            event_class = AlarmEvent

        if event_class:
            return event_class(self.event).build_message()

        message = SlackMessage()

        if isinstance(self.message, dict):
            # If message is a dict, split attributes into attachment fields
            attachment = SlackAttachment(
                title=self.subject,
                text=None,
            )

            for key, value in self.message.items():
                short = True

                # If value is a list/dict, convert to JSON and use full width field
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                    short = False

                # Add the field
                attachment.add_field(
                    title=key,
                    value=value,
                    short=short
                )

            # Add attachment to the message
            message.add_attachment(attachment)

        else:
            # Fallback to a plain message
            message.text = '*%(subject)s*\n\n%(message)s' % {
                'subject': self.subject,
                'message': self.message
            }

        return message
