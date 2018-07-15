from events.cloudwatch import CloudWatchEvent
from slack import SlackMessage, SlackAttachment
from utils import build_phd_link


class HealthEvent(CloudWatchEvent):

    def __init__(self, event):
        super(HealthEvent, self).__init__(event)
        self.service = self.detail['service']

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
