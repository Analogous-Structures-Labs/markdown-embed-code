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
            pattern = r"\s*(?P<file_path>.+\S)(?:\s*\[\s*(?P<start_at>\d*)\s*(?P<has_colon>:)?\s*(?P<end_at>\d*)?\s*\])"
            file_path, start_at, has_colon, end_at = match(pattern, extra).group(
                "file_path", "start_at", "has_colon", "end_at"
            )
            start_at = int(start_at) if start_at.isdigit() else None
            end_at = int(end_at) if end_at.isdigit() else None

            if not start_at and not end_at:
                start_at = 1
            else:
                start_at = start_at or 1

                if not has_colon:
                    end_at = start_at + 1
        except AttributeError:
            file_path, start_at, end_at = extra, 1, None

        return cls(
            file_path=Path(file_path),
            start_at=start_at,
            end_at=end_at,
        )

    def __iter__(self):
        with self.file_path.open() as file:
            for line in islice(
                file, self.start_at - 1, self.end_at - 1 if self.end_at else None
            ):
                yield f"{line}\n" if line[-1] != "\n" else line

    def __str__(self) -> str:
        return "".join(self)


class MarkdownEmbedCodeRenderer(MarkdownRenderer):
    def render_fenced_code(self, element):
        if element.__dict__["extra"]:
            element.children[0].children = str(
                Embed.parse_from_extra(element.__dict__["extra"])
            )

        return super().render_fenced_code(element)

    def render_image(self, element):
        template = "![{}]({}{})"
        title = (
            ' "{}"'.format(element.title.replace('"', '\\"')) if element.title else ""
        )
        return template.format(self.render_children(element), element.dest, title)


_markdown = Markdown(renderer=MarkdownEmbedCodeRenderer)


def render_markdown(contents: str):
    return _markdown(contents)


def render_markdown_file(file_path: Path):
    with file_path.open("r+") as file:
        rendered_contents = _markdown(file.read())
        file.seek(0)
        file.write(rendered_contents)
        file.truncate()
