"""Action Source code."""
import os
import requests
import github

# from pprint import pprint

# required to run the script locally
# from os.path import join, dirname
# from dotenv import load_dotenv

# dotenv_path = join(dirname(__file__), "../.env")
# load_dotenv(dotenv_path)


def count_issues(author, token, repo):
    """
    Count the number of open Issues created by a contributor of the project.

    author : Github id of the contributor
    assignee : Github id of the assigned contributor
    token : Github Token
    repo : Reository for which we are retriving the count
    """
    query_url = f"https://api.github.com/search/issues?q=is:issue+repo:{repo}+assignee:{author}+is:open"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(query_url, headers=headers)
    raw = r.json()
    return raw["total_count"]


def get_latest_issue(author, token, repo):
    r"""
    Get the contributor's latest Open Issue.

    author : Github id of the author of issue
    assignee : Github id of the assigned contributor
    token : Github Token
    repo : Reository for which we are retriving the count
    """
    query_url = f"https://api.github.com/search/issues?q=is:issue+repo:{repo}+assignee:{author}+is:open"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(query_url, headers=headers)
    raw = r.json()
    k = raw["items"]
    k = k[0]
    label_count = len(k["labels"])
    if label_count != 0:
        for i in range(label_count):
            if "on-review" in k["labels"][i]["name"]:
                return None
    return k["number"]


def reassign_issue(num, repo, maxi):
    r"""
    Close the issue and add a comment to the issue stating the reason.

    num : number of the issue that has to be closed
    repo : Reository for which we are retriving the count
    maxi : Maximium count of open Issue a contributor can have
    """
    issue = repo.get_issue(num)
    issue.create_comment(
        """The assigned contributor has more than """
        + str(maxi)
        + """ open issues, kindly reassign manually (@Supervisors/Mentors)"""
    )
    issue.edit(assignees=[])
    labels_temp = get_labels()
    labels_temp.remove("Assigned")
    issue.edit(labels=labels_temp)
    return


token = os.environ["INPUT_TOKEN"]
author = os.environ["INPUT_AUTHOR"]
repourl = os.environ["INPUT_REPO"]
maxi = os.environ["INPUT_MAXISSUE"]

if maxi is None:
    maxim = 3
else:

    maxim = int("".join(c for c in maxi if c.isdigit()))

github = github.Github(token)
repo = github.get_repo(repourl)

count = count_issues(author=author, token=token, repo=repourl)

numb = get_latest_issue(author=author, token=token, repo=repourl)
if numb is not None:
    if count >= maxim + 1:
        reassign_issue(numb, repo, maxim)
