import subprocess
import sys

from pathlib import Path
from typing import List

from pydantic import BaseSettings, SecretStr

from markdown_embed_code import convert


class Settings(BaseSettings):
    github_actor: str
    github_head_ref: str
    github_ref: str
    github_repository: str
    input_markdown: Path = Path("README.md")
    input_message: str = "Embed code into Markdown"
    input_no_change: str = "No changes were made!"
    input_output: Path = Path("")
    input_silent: bool = False
    input_token: SecretStr


def run_command(command: List, **kwargs):
    return subprocess.run(
        command,
        check=True,
        **kwargs,
    )


settings = Settings()

run_command(["git", "config", "--local", "user.name", "github-actions"])
run_command(["git", "config", "--local", "user.email", "github-actions@github.com"])

ref = settings.github_head_ref or settings.github_ref

if ref is None:
    sys.exit(1)

for path in Path(".").glob(str(settings.input_markdown)):
    with open(path, "r+") as f:
        embedded_doc = convert(f.read())

        f.seek(0)
        f.write(embedded_doc)
        f.truncate()

        run_command(["git", "add", path])

proc = run_command(
    ["git", "status", "--porcelain"],
    stdout=subprocess.PIPE,
)

if not proc.stdout:
    sys.exit(0)

run_command(["git", "commit", "-m", settings.input_message])

remote_repo = f"https://{settings.github_actor}:{settings.input_token.get_secret_value()}@github.com/{settings.github_repository}.git"
proc = run_command(["git", "push", remote_repo, f"HEAD:{ref}"])

if proc.returncode != 0:
    sys.exit(1)
