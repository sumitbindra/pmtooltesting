# github_integration.py
import os
import httpx

GITHUB_API_URL = "https://api.github.com"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_REPO_OWNER")
REPO = os.getenv("GITHUB_REPO_NAME")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

async def create_github_issue(title, body):
    url = f"{GITHUB_API_URL}/repos/{OWNER}/{REPO}/issues"
    data = {"title": title, "body": body}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_open_issues():
    url = f"{GITHUB_API_URL}/repos/{OWNER}/{REPO}/issues"
    params = {"state": "open"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
