# markdown-embed-code

[![tests](https://github.com/Analogous-Structures-Labs/markdown-embed-code/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/Analogous-Structures-Labs/markdown-embed-code/actions/workflows/build_and_test.yml)

Allows you to "import" code into your markdown files from elsewhere in your repository without having to manually copy and paste.
Supports code blocks in any language. Your original markdown file(s) will be overwritten with the rendered content.

Originally Forked from and inspired by [https://github.com/tokusumi/markdown-embed-code](https://github.com/tokusumi/markdown-embed-code) which appears to have been abandoned, enough has changed for this to be considered separate and no longer a drop in replacement. The general purpose and structure remain the same. The below list covers most of what has changed:

* Some bugs were fixed along the way and, more than likely, new ones were introduced.
* Features related to auto-commenting on PRs and rendering markdown files to different paths have been removed, at least for he time being.
* Instead of using a colon (:) to separate that syntax highlighting language for the embed directive, we now use a space. The colon has significance in some syntax highlighting grammars. Using it as a separator breaks syntax highlighting with those grammars.
* Syntax is loosely based on Python List access and slicing as closely as possible. The following notable differences should be considered:
  * Line numbers are one-based (start at 1) instead of zero-based, the former being widely accepted when numbering lines in a file and the latter being the standard way to enumerate iterable objects in most programming language.
  * Negative indexing is not supported.
  * Referencing a line number beyond the end of he file doesn't presently generate an error.
* You can now provide a path to a single file, a directory, or a glob pattern when targeting your markdown, making it possible to process multiple files.
* Parsing is now handled using regular expressions which should be both cleaner, more reliable, and more flexible.
* Interaction with git is now doing using [https://github.com/gitpython-developers/GitPython](GitPython) instead of running git commands via subprocess.

## Usage

### Embedding Entire files

In markdown, reference your file as follows in an otherwise empty code block.

````markdown
```python tests/src/sample.py

```
````

The action reads in the content from `tests/src/sample.py` and inserts its contents into your code block like so:

```python tests/src/sample.py
```

Any contents within your code block will be overwritten. Paths are relative to the root of your repository and not the directory containing the file being processed.

### Embedding Snippets

You can pull in a snippet from a file by including a range of line numbers like so:

````markdown
```python tests/src/sample.py [4:6]

```
````

Which will render the following output.

```python tests/src/sample.py [4:6]
```

The following are all valid ways to specify a snippet:

| syntax  | effect                                       |
| ------- | -------------------------------------------- |
| [5:10]  | Only lines 5 up until 10.                    |
| [5:]    | From line 5 through the end of the file.     |
| [:10]   | Everything up until line 10.                 |
| [5]     | Line 5 and only line 5.                      |
| [:], [] | All lines, equivalent of specifying nothing. |


### Workflow setup

Process README.md, import any referenced code, and push to your repo if there are any changes.

```yaml
name: Embed code in README

on:
  pull_request:
    branches:
      - main

jobs:
  embed-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          persist-credentials: false # otherwise, the token used is the GITHUB_TOKEN, instead of your personal token
          fetch-depth: 0 # otherwise, you will failed to push refs to dest repo
          ref: ${{ github.head_ref }}

      - uses: analogous-structures-labs/markdown-embed-code@main
        with:
          markdown: "README.md"
          message: "Synchronize Readme."
          token: ${{ secrets.GITHUB_TOKEN }}
```

### Configuration

| input                | description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| token                | Token for the repo. Can be passed in using `{{ secrets.GITHUB_TOKEN }}`. |
| markdown (Optional)  | Target path for your markdown file(s). (default: "README.md")            |
| message (Optional)   | Commit message for action. (default: "Embed code into Markdown.")        |


### Specifying your markdown path

The value provided for the `markdown` parameter supports specifying directories and glob patterns.
"README.md" will process only the top level README.
"some_dir" will process any files in some_dir with .md as their file extension.
"some_dir/README.md" will process only the README file within some_dir.
"\*\*/README.md" will process any markdown files named README.md, recursively through your repository.
"\*\*/*.md" will process any markdown files with .md as their file extension, recursively through your repository.
