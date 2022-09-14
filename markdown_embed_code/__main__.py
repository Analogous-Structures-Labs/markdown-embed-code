import subprocess
import sys
from pathlib import Path
from typing import List, Optional

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


def run_command(command: List, **kwargs):
    subprocess.run(
        command,
        check=True,
        **kwargs,
    )


settings = Settings()

run_command(["git", "config", "--local", "user.name", "github-actions"])
run_command(["git", "config", "--local", "user.email", "github-actions@github.com"])

repo = Github(settings.input_token.get_secret_value()).get_repo(settings.github_repository)

if not settings.github_event_path.is_file():
    sys.exit(1)
contents = settings.github_event_path.read_text()
print(contents)
event = PartialGitHubEvent.parse_raw(contents)

number = None
if event.number is not None:
    number = event.number
elif event.inputs and event.inputs.number:
    number = event.inputs.number

# Ignore already merged PRs.
if number and repo.get_pull(number).merged:
    sys.exit(0)

for path in Path(".").glob(str(settings.input_markdown)):
    with open(path, "r+") as f:
        doc = f.read()
        md = get_code_emb()
        embedded_doc = md(doc)

        f.seek(0)
        f.write(embedded_doc)

        output_path = path
        if settings.input_output.is_dir():
            output_path = f'{settings.input_output}/{path}'

        run_command(["git", "add", output_path])

proc = run_command(
    ["git", "status", "--porcelain"],
    stdout=subprocess.PIPE,
)

if not proc.stdout:
    # no change
    if not settings.input_silent:
        pr.create_issue_comment(settings.input_no_change)
    sys.exit(0)

run_command(["git", "commit", "-m", settings.input_message])

remote_repo = f"https://{settings.github_actor}:{settings.input_token.get_secret_value()}@github.com/{settings.github_repository}.git"
proc = run_command(["git", "push", remote_repo, f"HEAD:{pr.head.ref}"])

if proc.returncode != 0:
    sys.exit(1)
