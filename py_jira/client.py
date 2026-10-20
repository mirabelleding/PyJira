import os
from pathlib import Path
import requests

from .models import Issue


def adf(text):
    return {
        "type": "doc",
        "version": 1,
        "content": [{
            "type": "paragraph",
            "content": [{
                "type": "text",
                "text": text,
            }],
        }],
    }


class JiraClient:

    def __init__(self, base_url, username, token):
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.auth = (username, token)
        self.session.verify = False

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    @classmethod
    def from_env(cls):
        secrets_dir = Path(os.environ["JIRA_CONFIG"])

        return cls(
            base_url=(secrets_dir / "url").read_text().strip(),
            username=(secrets_dir / "username").read_text().strip(),
            token=(secrets_dir / "token").read_text().strip(),
        )
    

    def _get(self, key):
        response = self.session.get(
            f"{self.base_url}/rest/api/3/issue/{key}"
        )

        response.raise_for_status()
        return response.json()


    def get(self, key):
        return Issue(self, self._get(key))


    def search(self, jql):
        response = self.session.post(
            f"{self.base_url}/rest/api/3/search/jql",
            json={"jql": jql},
        )

        response.raise_for_status()

        return [
            Issue(self, data)
            for data in response.json()["issues"]
        ]


    def create(
        self,
        project,
        issue_type,
        summary,
        description=None,
        **fields,
    ):
        fields = {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
            "summary": summary,
            **fields,
        }

        if description:
            fields["description"] = adf(description)

        response = self.session.post(
            f"{self.base_url}/rest/api/3/issue",
            json={"fields": fields},
        )

        response.raise_for_status()

        return self.get(response.json()["key"])


    def update(self, key, **fields):
        if "description" in fields:
            fields["description"] = adf(
                fields["description"]
            )

        response = self.session.put(
            f"{self.base_url}/rest/api/3/issue/{key}",
            json={"fields": fields},
        )

        response.raise_for_status()


    def comment(self, key, text):
        response = self.session.post(
            f"{self.base_url}/rest/api/3/issue/{key}/comment",
            json={"body": adf(text)},
        )

        response.raise_for_status()


    def transitions(self, key):
        response = self.session.get(
            f"{self.base_url}/rest/api/3/issue/{key}/transitions"
        )

        response.raise_for_status()
        return response.json()["transitions"]


    def transition(self, key, name):
        transitions = self.transitions(key)

        transition = next(
            t for t in transitions
            if t["name"].lower() == name.lower()
        )

        response = self.session.post(
            f"{self.base_url}/rest/api/3/issue/{key}/transitions",
            json={
                "transition": {
                    "id": transition["id"]
                }
            },
        )

        response.raise_for_status()