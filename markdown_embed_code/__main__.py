from git import Actor, Repo
from pathlib import Path
from subprocess import run
from sys import exit
from typing import List

from pydantic import BaseSettings, SecretStr

from markdown_embed_code import render


class Settings(BaseSettings):
    github_actor: str
    github_head_ref: str
    github_ref: str
    github_repository: str
    github_workspace: str
    input_markdown: str = "README.md"
    input_message: str = "Embed code into Markdown."
    input_token: SecretStr


def run_command(command: List, **kwargs):
    return run(
        command,
        check=True,
        **kwargs,
    )


def overwrite_file(file_handle, new_contents):
    file_handle.seek(0)
    file_handle.write(new_contents)
    file_handle.truncate()


settings = Settings()

# The checkout action checks out code as the runner user (1001:121). Our docker image runs as root
# as recommended by the GitHub actions documentation. For that reason, we're ensuring he the user
# running the script owns the workspace. Otherwise, the subsequent git commands will fail.
#run_command("chown -R $(id -u):$(id-g) .", shell=True)

ref = settings.github_head_ref or settings.github_ref

if not ref:
    exit(1)

actor = Actor(settings.github_actor, "github-actions@github.com")
remote_repo_url = f"https://{settings.github_actor}:{settings.input_token.get_secret_value()}@github.com/{settings.github_repository}.git"
repo = Repo(".")

with repo.config_writer() as git_config:
    git_config.set_value("global", "safe.directory", settings.github_workspace)
    git_config.set_value('user', 'name', settings.github_actor)
    git_config.set_value('user', 'email', "github-actions@github.com")

repo.remotes.origin.set_url(remote_repo_url)

if Path(settings.input_markdown).is_dir():
    settings.input_markdown = f'{settings.input_markdown}/*.md'

for file_path in Path(".").glob(settings.input_markdown):
    with file_path.open("r+") as file:
        overwrite_file(file, render(file.read()))
        repo.index.add(file_path)

if repo.is_dirty(untracked_files=True):
    repo.index.commit(
        settings.input_message,
        author=actor,
        committer=actor,
    )
    repo.remotes.origin.push(f"HEAD:{ref}").raise_if_error()
else:
    print("No changes to commit.")
