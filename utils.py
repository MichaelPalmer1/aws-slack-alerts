import os


def get_region():
    return os.environ['AWS_REGION']


def build_ec2_search(query, method='search', region=None):
    """
    Build EC2 search url

    :param str query: Query parameters
    :param str method: Search method
    :param str region: AWS Region
    :return: URL
    :rtype: str
    """
    if not region:
        region = get_region()

    return 'https://console.aws.amazon.com/ec2/v2/home?region=%(region)s#Instances:%(method)s=%(query)s' % {
        'region': region,
        'method': method,
        'query': query
    }


def build_asg_link(group_name, region=None):
    """
    Build auto scaling group url

    :param str group_name: Auto scaling group name
    :param str region: AWS Region
    :return: URL
    :rtype: str
    """
    if not region:
        region = get_region()

    return 'https://console.aws.amazon.com/ec2/autoscaling/home?region=%(region)s#AutoScalingGroups:' \
           'id=%(asg)s;view=history' % \
           {
               'region': region,
               'asg': group_name
           }


def build_alarm_link(alarm_name, region=None):
    """
    Build alarm url

    :param str alarm_name: Alarm name
    :param str region: AWS Region
    :return: URL
    :rtype: str
    """
    if not region:
        region = get_region()

    return 'https://console.aws.amazon.com/cloudwatch/home?region=%(region)s#alarm:alarmFilter=ANY;name=%(alarm)s' % {
        'region': region,
        'alarm': alarm_name
    }
