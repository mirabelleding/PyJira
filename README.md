# PyJira

A lightweight Python client for the Jira REST API, providing an object-oriented interface for issue retrieval, JQL search, creation, updates, comments, and workflow transitions.

## Setup
Create a directory containing the Jira connection details:

```text
jira_config/
├── url
├── username
└── token
```

```bash
export JIRA_CONFIG="/path/to/jira_config"
```

## Usage
```python
# get an issue
issue = jira.get("MI77-7")

print(issue.key)
print(issue.summary)
print(issue.status)
print(issue.assignee)
```
```python
# search issues using native Jira Query Language (JQL)
issues = jira.search("""
    project = MI77
    AND statusCategory != Done
    ORDER BY updated DESC
""")

for issue in issues:
    print(issue.key, issue.summary, issue.status)
```
```python
# search by text
issues = jira.search("""
    project = MI77
    AND text ~ "some inspirations and a little magic"
""")
```
```python
# create an issue
issue = jira.create(
    project="MI77",
    issue_type="py_jira",
    summary="Automate this boring Jira thing",
    description=(
        "Support issue lookup, JQL search, ticket creation, comments, "
        "updates, and workflow transitions from Python. "
        "And most importantly.. no more dealing with a frontend. "
    )
)

print(issue.key)
```
```python
# Update an issue
issue = jira.get("MI77-7")

issue.update(
    summary="tryin' to make Jira less painful"
)
```
```python
# Add comment
issue.comment(
    "still hating Jira, but at least now it feels like a backend work."
)
```
```python
# Transition an issue
issue.transition("In Progress")
issue.transition("Done")
```
```python
# Refresh an issue
issue.refresh()

print(issue.status)
```