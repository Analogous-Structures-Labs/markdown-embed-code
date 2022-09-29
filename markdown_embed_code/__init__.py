from __future__ import annotations

import re

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Optional

from marko import Markdown
from marko.md_renderer import MarkdownRenderer


Lines = Iterator[str]


def slice_file(
    file_path: Path,
    starting_at: Optional[int] = 1,
    ending_at: Optional[int] = None,
) -> Lines:
    with file_path.open() as file:
        for line_number, line in enumerate(file):
            if ending_at and line_number == ending_at:
                break
            if line_number >= starting_at - 1:
                yield f"{line}\n" if line[-1] != "\n" else line


def safe_int(castee: Any, default: Any) -> Union[int, None]:
    try:
        return int(castee)
    except (TypeError, ValueError):
        return default


@dataclass
class Embed:
    file_path: Path
    start_line_number: int
    end_line_number: Optional[int]

    @classmethod
    def from_string(cls, embed_string: str) -> Embed:
        try:
            path, start_at, end_at = embed_string, 1, None
            path, start_at, *_ = re.split(r"\[([\d\s\-:]*)\]", embed_string, maxsplit=1)
            start_at, end_at = re.split(r"-|:", start_at, maxsplit=1)
        except ValueError:
            pass

        return cls(
            file_path=Path(path.strip()),
            start_line_number=safe_int(start_at, 1) or 1,
            end_line_number=safe_int(end_at, None),
        )

    @property
    def code(self) -> str:
        return ''.join(
            slice_file(
                file_path = self.file_path,
                starting_at=self.start_line_number,
                ending_at=self.end_line_number,
            )
        )


class MarkdownEmbCodeRenderer(MarkdownRenderer):
    def render_fenced_code(self, element):
        try:
            ed = element.__dict__
            fenced_code_parameters = f'{ed.get("lang").rsplit(":", 1)[1]}{ed.get("extra", "")}'
            element.children[0].children = Embed.from_string(fenced_code_parameters).code
        except IndexError:
            pass

        return super().render_fenced_code(element)

    def render_image(self, element):
        template = "![{}]({}{})"
        title = (
            ' "{}"'.format(element.title.replace('"', '\\"')) if element.title else ""
        )
        return template.format(self.render_children(element), element.dest, title)


_markdown = Markdown(renderer=MarkdownEmbCodeRenderer)


def render(document: str):
    return _markdown(document)
