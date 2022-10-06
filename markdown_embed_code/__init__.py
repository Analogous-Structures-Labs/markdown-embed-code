from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from re import match
from typing import Optional

from marko import Markdown
from marko.md_renderer import MarkdownRenderer


@dataclass
class Embed(Iterable):
    file_path: Path
    start_at: int
    end_at: Optional[int]

    @classmethod
    def parse_from_extra(cls, extra: str) -> Embed:
        try:
            pattern = r"\s*(?P<file_path>.+\S)(?:\s*\[\s*(?P<start_at>\d*)\s*(?P<colon>:)?\s*(?P<end_at>\d*)?\s*\])"
            file_path, start_at, colon, end_at = match(pattern, extra).group("file_path", "start_at", "colon", "end_at")
        except AttributeError:
            file_path, start_at, colon, end_at = extra, 1, None, None

        start_at = int(start_at or 1) or 1
        end_at = start_at if not colon else (int(end_at) if end_at else None)

        return cls(
            file_path=Path(file_path),
            start_at=start_at,
            end_at=end_at,
        )

    def __iter__(self):
        with self.file_path.open() as file:
            for line in islice(file, self.start_at - 1, self.end_at):
                yield f"{line}\n" if line[-1] != "\n" else line

    def __str__(self) -> str:
        return ''.join(self)


class MarkdownEmbedCodeRenderer(MarkdownRenderer):
    def render_fenced_code(self, element):
        if element.__dict__["extra"]:
            element.children[0].children = str(Embed.parse_from_extra(element.__dict__["extra"]))

        return super().render_fenced_code(element)

    def render_image(self, element):
        template = "![{}]({}{})"
        title = (
            ' "{}"'.format(element.title.replace('"', '\\"')) if element.title else ""
        )
        return template.format(self.render_children(element), element.dest, title)


_markdown = Markdown(renderer=MarkdownEmbedCodeRenderer)


def render_markdown(document: str) -> str:
    return _markdown(document)


def render_markdown_file(file_path: Path):
    with file_path.open("r+") as file:
        rendered_contents = render_markdown(file.read())
        file.seek(0)
        file.write(rendered_contents)
        file.truncate()
