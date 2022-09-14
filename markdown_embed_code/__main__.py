import subprocess
import sys
from pathlib import Path
from typing import Optional

from github import Github
from pydantic import BaseModel, BaseSettings, SecretStr

from markdown_embed_code import get_code_emb


class Settings(BaseSettings):
    input_markdown: Path = Path("README.md")
    input_message: str = "📝 Update Readme"
    input_no_change: str = "No changes on README!"
    input_output: Path = Path("")
    input_silent: bool = False
    input_token: SecretStr
    github_actor: str
    github_repository: str
    github_event_path: Path


class PartialGitHubEventInputs(BaseModel):
    number: int


class PartialGitHubEvent(BaseModel):
    number: Optional[int] = None
    inputs: Optional[PartialGitHubEventInputs] = None


settings = Settings()

print(settings.input_markdown)

default_subprocess_args = {
    'check': True,
}

subprocess.run(
    ["/usr/bin/git", "config", "--local", "user.name", "github-actions"],
    **default_subprocess_args,
)
subprocess.run(
    ["/usr/bin/git", "config", "--local", "user.email", "github-actions@github.com"],
    **default_subprocess_args,
)

g = Github(settings.input_token.get_secret_value())
repo = g.get_repo(settings.github_repository)

if not settings.github_event_path.is_file():
    print("exit 1")
    sys.exit(1)
contents = settings.github_event_path.read_text()
event = PartialGitHubEvent.parse_raw(contents)

if event.number is not None:
    number = event.number
elif event.inputs and event.inputs.number:
    number = event.inputs.number
else:
    print("exit 2")
    sys.exit(1)

# Ignore already merged PRs.
if repo.get_pull(number).merged:
    print("exit 3")
    sys.exit(0)

print("loop time")
print(settings.input_markdown)

for path in Path(".").glob(settings.input_markdown):
    with open(path, "r+") as f:
        doc = f.read()
        md = get_code_emb()
        embedded_doc = md(doc)

        f.seek(0)
        f.write(embedded_doc)

        output_path = path

        if settings.input_output.is_dir():
            output_path = f'{settings.input_output}/{path}'

        subprocess.run(
            ["/usr/bin/git", "add", output_path],
            **default_subprocess_args,
        )

proc = subprocess.run(
    ["/usr/bin/git", "status", "--porcelain"],
    stdout=subprocess.PIPE,
    **default_subprocess_args,
)

if not proc.stdout:
    # no change
    if not settings.input_silent:
        pr.create_issue_comment(settings.input_no_change)
    sys.exit(0)

subprocess.run(
    ["/usr/bin/git", "commit", "-m", settings.input_message],
    **default_subprocess_args,
)

remote_repo = f"https://{settings.github_actor}:{settings.input_token.get_secret_value()}@github.com/{settings.github_repository}.git"
proc = subprocess.run(
    ["/usr/bin/git", "push", remote_repo, f"HEAD:{pr.head.ref}"],
    **default_subprocess_args,
)

if proc.returncode != 0:
    sys.exit(1)
