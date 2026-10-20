from dataclasses import dataclass

@dataclass
class Issue:
    client: object
    data: dict

    @property
    def key(self):
        return self.data["key"]

    @property
    def fields(self):
        return self.data["fields"]

    @property
    def summary(self):
        return self.fields["summary"]

    @property
    def status(self):
        return self.fields["status"]["name"]

    @property
    def assignee(self):
        assignee = self.fields.get("assignee")
        return assignee["displayName"] if assignee else None


    def refresh(self):
        self.data = self.client._get(self.key)
        return self


    def update(self, **fields):
        self.client.update(self.key, **fields)
        return self.refresh()


    def comment(self, text):
        self.client.comment(self.key, text)
        return self


    def transition(self, name):
        self.client.transition(self.key, name)
        return self.refresh()