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
    completed_process = subprocess.run(
        command,
        check=True,
        **kwargs,
    )

    completed_process.check_returncode()
    return completed_process

def overwrite_file(file_handle, new_contents):
    file_handle.seek(0)
    file_handle.truncate()
    file_handle.write(new_contents)


try:
    settings = Settings()

    run_command(["git", "config", "--local", "user.name", "github-actions"])
    run_command(["git", "config", "--local", "user.email", "github-actions@github.com"])

    ref = settings.github_head_ref or settings.github_ref

    if not ref:
        sys.exit(1)

    for path in Path(".").glob(str(settings.input_markdown)):
        with open(path, "r+") as f:
            overwrite_file(f, convert(f.read()))
            run_command(["git", "add", path])

    git_status_output = run_command(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
    ).stdout

    if git_status_output:
        run_command(["git", "commit", "-m", settings.input_message])
        remote_repo = f"https://{settings.github_actor}:{settings.input_token.get_secret_value()}@github.com/{settings.github_repository}.git"
        run_command(["git", "push", remote_repo, f"HEAD:{ref}"])

except subprocess.CalledProcessError:
    sys.exit(1)
