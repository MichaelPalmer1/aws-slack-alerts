import json

from .base import Event


class SNSEvent(Event):

    def __init__(self, event):
        super(SNSEvent, self).__init__(event)
        self.sns = self.event['Records'][0]['Sns']
        self.topic = self.sns['TopicArn']
        topic_parts = self.topic.split(':')
        self.account_id = topic_parts[4]
        self.region = topic_parts[3]
        self.subject = self.sns['Subject']
        self.message = json.loads(self.sns['Message'])
        self.event_type = self.message['Event']
        self.service = self.event_type.split(':')[0]

    def build_message(self):
        if self.service == 'autoscaling':
            from events.autoscaling import AutoScalingEvent
            return AutoScalingEvent(self.event).build_message()
