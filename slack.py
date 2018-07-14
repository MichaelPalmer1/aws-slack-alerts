class SlackMessage:
    attachments = []

    def add_attachment(self, attachment):
        """
        Add an attachment to the message

        :param SlackAttachment attachment: Attachment
        """
        self.attachments.append(attachment.build())

    def build(self):
        return {
            'attachments': self.attachments
        }


class SlackAttachment:
    fields = []

    def __init__(self, title, text, fallback=None, color='', footer=None):
        self.title = title
        self.text = text
        self.fallback = fallback or self.title
        self.color = color
        self.footer = footer

    def add_field(self, title, value, short=True):
        self.fields.append({
            'title': title,
            'value': value,
            'short': short
        })

    def build(self):
        return {
            'title': self.title,
            'text': self.text,
            'fallback': self.fallback,
            'footer': self.footer,
            'color': self.color,
            'fields': self.fields
        }
