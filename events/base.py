from abc import abstractmethod

import boto3


class Event:

    def __init__(self, event):
        self.event = event
        self._session = boto3.Session()

    @abstractmethod
    def build_message(self):
        raise NotImplementedError
