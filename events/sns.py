import json

from .base import Event


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
        event_class = SNSEvent

        if 'AutoScalingGroupARN' in self.message:
            from events.autoscaling import AutoScalingEvent
            event_class = AutoScalingEvent

        elif 'AlarmName' in self.message:
            from events.alarm import AlarmEvent
            event_class = AlarmEvent

        if event_class != SNSEvent:
            return event_class(self.event).build_message()
