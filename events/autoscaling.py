from botocore.exceptions import ClientError

from slack import SlackMessage, SlackAttachment
from utils import build_asg_link, build_ec2_search

from . import event_types
from .sns import SNSEvent


class AutoScalingEvent(SNSEvent):

    VALID_EVENTS = [
        event_types.EVENT_AUTOSCALING_INSTANCE_LAUNCH,
        event_types.EVENT_AUTOSCALING_INSTANCE_TERMINATE,
        event_types.EVENT_AUTOSCALING_LAUNCH_ERROR,
        event_types.EVENT_AUTOSCALING_TERMINATE_ERROR
    ]

    def __init__(self, event):
        super(AutoScalingEvent, self).__init__(event)
        self.ec2 = self._session.resource('ec2')

        # Attempt to resolve the account alias
        self.account_alias = None
        if self.account_id == self.message['AccountId']:
            try:
                account_aliases = self._session.client('iam').list_account_aliases()
                self.account_alias = account_aliases['AccountAliases'][0]
            except ClientError:
                pass

    def build_message(self):
        if self.event_type not in self.VALID_EVENTS:
            return

        if self.event_type == event_types.EVENT_AUTOSCALING_INSTANCE_LAUNCH:
            color = 'good'
        elif self.event_type == event_types.EVENT_AUTOSCALING_INSTANCE_TERMINATE:
            color = 'warning'
        else:
            color = 'danger'

        message = SlackMessage()
        attachment = SlackAttachment(
            title=self.subject,
            text=self.message['Cause'].replace('  ', '.\n\n'),
            footer=self.message['Service'],
            color=color,
        )

        # Auto Scaling Group
        asg_name = self.message['AutoScalingGroupName']
        attachment.add_field(
            title='Auto Scaling Group Name',
            value='<%s|%s>' % (build_asg_link(asg_name, region=self.region), asg_name)
        )

        # Instance ID
        instance_id = self.message['EC2InstanceId']
        attachment.add_field(
            title='EC2 Instance ID',
            value='<%s|%s>' % (build_ec2_search(instance_id, method='instanceId', region=self.region), instance_id)
        )

        # Subnet
        subnet_id = self.message['Details'].get('Subnet ID')
        subnet_name = subnet_id
        try:
            subnet = self.ec2.Subnet(subnet_id)
            for item in subnet.tags:
                if item['Key'] == 'Name':
                    subnet_name = item['Value']
                    break
        except ClientError:
            subnet = None

        # Availability Zone
        availability_zone = self.message['Details'].get('Availability Zone')

        # Combine subnet and availability zone into a single field
        attachment.add_field(
            title='Subnet',
            value='<%s|%s (%s)>' % (
                build_ec2_search(subnet_id, method='subnetId', region=self.region),
                subnet_name,
                availability_zone
            )
        )

        # Get VPC if possible
        if subnet:
            vpc_name = subnet.vpc.id
            for item in subnet.vpc.tags:
                if item['Key'] == 'Name':
                    vpc_name = item['Value']
                    break

            attachment.add_field(
                title='VPC',
                value='<%s|%s>' % (build_ec2_search(subnet.vpc.id, method='vpcId', region=self.region), vpc_name),
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

        # Region Information
        attachment.add_field(
            title='Region',
            value=self.region
        )

        # Add the attachment
        message.add_attachment(attachment)
        return message
