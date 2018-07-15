import json

from slack import SlackAttachment, SlackMessage
from .base import Event


class CloudWatchEvent(Event):

    def __init__(self, event):
        super(CloudWatchEvent, self).__init__(event)
        self.source = self.event['source']
        self.detail = self.event['detail']
        self.detail_type = self.event['detail-type']
        self.resources = self.event['resources']
        self.account_id = self.event['account']
        self.region = self.event['region']

    def build_message(self):
        event_class = None

        # Handle supported event types
        if self.source == 'aws.health':
            from events.health import HealthEvent
            event_class = HealthEvent

        if event_class:
            return event_class(self.event).build_message()

        # Create message and attachment
        message = SlackMessage(
            text=self.detail_type,
        )
        attachment = SlackAttachment(
            title=self.detail_type,
            text=json.dumps(self.detail),
            footer='CloudWatch Event'
        )

        # Source
        attachment.add_field(
            title='Source',
            value=self.source
        )

        # Account
        attachment.add_field(
            title='Account',
            value=self.account_id
        )

        # Region
        attachment.add_field(
            title='Region',
            value=self.region
        )

        # Resources
        if self.resources:
            attachment.add_field(
                title='Resources',
                value=', '.join(self.resources),
                short=False
            )

        # Add attachment
        message.add_attachment(attachment)
        return message
