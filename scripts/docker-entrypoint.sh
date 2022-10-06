#!/usr/bin/env sh -e

git config --global --add safe.directory $GITHUB_WORKSPACE
exec python -m markdown_embed_code
