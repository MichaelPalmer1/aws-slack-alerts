from slack import SlackMessage, SlackAttachment
from utils import build_phd_link
from .base import Event


class HealthEvent(Event):

    def __init__(self, event):
        super(HealthEvent, self).__init__(event)
        self.region = self.event['region']
        self.resources = self.event['resources']
        self.detail = self.event['detail']
        self.service = self.detail['service']
        self.account_id = self.event['account']

    def build_message(self):
        message = SlackMessage()

        # Build the text
        text = ''
        for item in self.detail['eventDescription']:
            text = item['latestDescription'] + '\n' + text

        # Create attachment
        attachment = SlackAttachment(
            title=self.detail['eventTypeCode'],
            title_link=build_phd_link(self.detail['eventArn']),
            text=text,
            footer='CloudWatch Event',
            color='danger'
        )

        # Service
        attachment.add_field(
            title='Service',
            value=self.service
        )

        # Region
        attachment.add_field(
            title='Region',
            value=self.region
        )

        # Affected resources
        attachment.add_field(
            title='Resources',
            value=', '.join(self.resources),
            short=False
        )

        # Account Information
        attachment.add_field(
            title='Account',
            value=self.account_id
        )

        # Add attachment and return message
        message.add_attachment(attachment)
        return message
