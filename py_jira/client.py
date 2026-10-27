import os
from pathlib import Path
from typing import Any, Self

import requests

from .issue import Issue


def adf(text: str) -> dict[str, Any]:
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

    def __init__(
        self,
        base_url: str,
        username: str,
        token: str,
        verify: bool | str = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")

        self.session = requests.Session()
        self.session.auth = (username, token)
        self.session.verify = verify

        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    @classmethod
    def from_env(
        cls,
        verify: bool | str = True,
    ) -> Self:
        secrets_dir = Path(os.environ["JIRA_CONFIG"])

        return cls(
            base_url=(secrets_dir / "url").read_text().strip(),
            username=(secrets_dir / "username").read_text().strip(),
            token=(secrets_dir / "token").read_text().strip(),
            verify=verify,
        )

    def _get(self, key: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/rest/api/3/issue/{key}"
        )

        response.raise_for_status()
        return response.json()

    def get(self, key: str) -> Issue:
        return Issue(self, self._get(key))

    def search(self, jql: str) -> list[Issue]:
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
        project: str,
        issue_type: str,
        summary: str,
        description: str | None = None,
        **fields: Any,
    ) -> Issue:
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

    def update(self, key: str, **fields: Any) -> None:
        if "description" in fields:
            fields["description"] = adf(
                fields["description"]
            )

        response = self.session.put(
            f"{self.base_url}/rest/api/3/issue/{key}",
            json={"fields": fields},
        )

        response.raise_for_status()

    def comment(self, key: str, text: str) -> None:
        response = self.session.post(
            f"{self.base_url}/rest/api/3/issue/{key}/comment",
            json={"body": adf(text)},
        )

        response.raise_for_status()

    def transitions(self, key: str) -> list[dict[str, Any]]:
        response = self.session.get(
            f"{self.base_url}/rest/api/3/issue/{key}/transitions"
        )

        response.raise_for_status()
        return response.json()["transitions"]

    def transition(self, key: str, name: str) -> None:
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
