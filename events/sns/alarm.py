from botocore.exceptions import ClientError

from events.sns import SNSEvent
from slack import SlackMessage, SlackAttachment
from utils import build_ec2_search, build_alarm_link


class AlarmEvent(SNSEvent):

    def __init__(self, event):
        super(AlarmEvent, self).__init__(event)
        self.alarm_name = self.message['AlarmName']
        self.trigger = self.message['Trigger']

        # Attempt to resolve the account alias
        self.account_alias = None
        if self.account_id == self.message['AWSAccountId']:
            try:
                account_aliases = self._session.client('iam').list_account_aliases()
                self.account_alias = account_aliases['AccountAliases'][0]
            except ClientError:
                pass

    def build_message(self):
        alarm_state = self.message['NewStateValue']
        if alarm_state == 'ALARM':
            color = 'danger'
        elif alarm_state == 'OK':
            color = 'good'
        else:
            color = 'warning'

        message = SlackMessage()
        attachment = SlackAttachment(
            title=self.subject,
            text=self.message['NewStateReason'],
            footer='CloudWatch Alarm',
            color=color
        )

        # Alarm
        attachment.add_field(
            title='Alarm',
            value='<%s|%s>' % (build_alarm_link(self.alarm_name, region=self.region), self.alarm_name)
        )

        # Build fields for each dimension
        for dimension in self.trigger['Dimensions']:
            title = dimension['name']
            value = dimension['value']

            # Add link to certain dimensions
            if title == 'InstanceId':
                value = '<%s|%s>' % (build_ec2_search(value, region=self.region, method='instanceId'), value)

            attachment.add_field(
                title=title,
                value=value
            )

        # Metric
        attachment.add_field(
            title='Metric',
            value='%s/%s' % (self.trigger['Namespace'], self.trigger['MetricName'])
        )

        # Account Information
        if self.account_alias:
            account = '%s (%s)' % (self.account_alias, self.account_id)
        else:
            account = self.account_id

        attachment.add_field(
            title='Account',
            value=account
        )

        # Region
        attachment.add_field(
            title='Region',
            value=self.message['Region']
        )

        # Add the attachment
        message.add_attachment(attachment)
        return message
