import json
import logging
import os

from urllib2 import Request, urlopen

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Event types
EVENT_INSTANCE_LAUNCH = 'autoscaling:EC2_INSTANCE_LAUNCH'
EVENT_INSTANCE_TERMINATE = 'autoscaling:EC2_INSTANCE_TERMINATE'
EVENT_LAUNCH_ERROR = 'autoscaling:EC2_INSTANCE_LAUNCH_ERROR'
EVENT_TERMINATE_ERROR = 'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'

# Define valid events
VALID_EVENTS = [
    EVENT_INSTANCE_LAUNCH,
    EVENT_INSTANCE_TERMINATE,
    EVENT_LAUNCH_ERROR,
    EVENT_TERMINATE_ERROR
]

# Environment variables
HOOK_URL = os.environ['HOOK_URL']
REGION = os.environ.get('AWS_REGION', 'us-west-2')


def lambda_handler(event, context):
    """
    Handle the lambda call

    :param dict event: Event data
    :param context: Lambda function context
    """
    logger.info("Event: %s", event)
    sns = event['Records'][0]['Sns']
    message = json.loads(sns['Message'])
    color = ''
    msg = None
    
    # Check if this is an alarm
    alarm_state = message.get('NewStateValue', 'ALARM')
    if alarm_state == 'ALARM':
        color = 'danger'
    elif alarm_state == 'OK':
        color = 'good'
    else:
        color = 'warning'

    msg = json.dumps(build_alarm_message(sns['Subject'], message, color))
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


def build_ec2_search(query, region=REGION):
    """
    Build EC2 search url

    :param str query: Query parameters
    :param str region: AWS Region
    :return: URL
    :rtype: str
    """
    url = 'https://%(region)s.console.aws.amazon.com/ec2/v2/home?region=%(region)s#Instances:search=%(query)s'
    return url % {'region': region, 'query': query}


def build_alarm_message(title, data, color=''):
    """
    Build an alarm message for Slack

    :param str title: Message title
    :param dict data: Message data
    :param str color: Attachment color
    :return: Slack message dict
    :rtype: dict
    """
    message = {
        'attachments': []
    }

    fields = []
    
    '''
  "AlarmName": "rancher-CPU-Utilization",
  "AlarmDescription": "Created from EC2 Console",
  "AWSAccountId": "011437889952",
  "NewStateValue": "ALARM",
  "NewStateReason": "Threshold Crossed: 2 datapoints were greater than or equal to the threshold (75.0). The most recent datapoints: [75.27138888888891, 77.3574647887324].",
  "StateChangeTime": "2017-01-31T07:52:18.940+0000",
  "Region": "US West - Oregon",
  "OldStateValue": "OK",
  "Trigger": {
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Statistic": "AVERAGE",
    "Unit": null,
    "Dimensions": [
      {
        "name": "InstanceId",
        "value": "i-288028bd"
      }
    ],
    "Period": 21600,
    "EvaluationPeriods": 2,
    "ComparisonOperator": "GreaterThanOrEqualToThreshold",
    "Threshold": 75.0
    '''

    # Instance ID
    for item in data['Trigger']['Dimensions']:
        if item['name'] == 'InstanceId':
            fields.append({
                'title': item['name'],
                'value': '<%s|%s>' % (build_ec2_search(item['value']), item['value']),
                'short': True
            })
        else:
            fields.append({
                'title': item['name'],
                'value': item['value'],
                'short': True
            })

    # Old State
    fields.append({
        'title': 'Old State',
        'value': data['OldStateValue'],
        'short': True
    })
    
    # New State
    fields.append({
        'title': 'New State',
        'value': data['NewStateValue'],
        'short': True
    })

    # Region
    fields.append({
        'title': 'Region',
        'value': data['Region'],
        'short': True
    })

    # Build the attachment and append it to the message
    attachment = {
        'fallback': title,
        'color': color,
        'title': title,
        'text': data['NewStateReason'],
        'fields': fields,
        'footer': 'CloudWatch Alarm'
    }
    message['attachments'].append(attachment)
    return message


def build_autoscaling_message(title, data, color=''):
    """
    Build an autoscaling message for Slack

    :param str title: Message title
    :param dict data: Message data
    :param str color: Attachment color
    :return: Slack message dict
    :rtype: dict
    """
    message = {
        'attachments': []
    }

    fields = []

    # Auto Scaling Group
    asg_link = 'https://%(region)s.console.aws.amazon.com/ec2/autoscaling/home?region=%(region)s#AutoScalingGroups:' \
               'id=%(asg)s;view=history' % {'region': REGION, 'asg': data['AutoScalingGroupName']}
    fields.append({
        'title': 'Auto Scaling Group Name',
        'value': '<%s|%s>' % (asg_link, data['AutoScalingGroupName']),
        'short': True
    })

    # EC2 Instance ID
    fields.append({
        'title': 'EC2 Instance ID',
        'value': '<%s|%s>' % (build_ec2_search(data['EC2InstanceId']), data['EC2InstanceId']),
        'short': True
    })

    # Subnet ID
    if 'Subnet ID' in data['Details']:
        fields.append({
            'title': 'Subnet ID',
            'value': '<%s|%s>' % (build_ec2_search(data['Details']['Subnet ID']), data['Details']['Subnet ID']),
            'short': True
        })

    # Availability Zone
    if 'Availability Zone' in data['Details']:
        fields.append({
            'title': 'Availability Zone',
            'value': '<%s|%s>' % (build_ec2_search(data['Details']['Availability Zone']),
                                  data['Details']['Availability Zone']),
            'short': True
        })

    # Build the attachment and append it to the message
    attachment = {
        'fallback': title,
        'color': color,
        'title': title,
        'text': data['Cause'].replace('  ', '.\n\n'),
        'fields': fields,
        'footer': data['Service']
    }
    message['attachments'].append(attachment)
    return message	