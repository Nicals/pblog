"""This extensions adds some meta data support to markdown.

```markdonw
---
foo: bar
bar:
    - baz
---
```
"""

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import yaml


__all__ = ['MetaExtension']


class MetaPreprocessor(Preprocessor):
    def run(self, lines):
        self.markdown.meta = None
        inside_meta = True
        meta = []
        new_lines = []

        if lines[0] != '---':
            return lines

        for line_nb, line in enumerate(lines):
            # skip first line as we already know it's the delimiter
            if line_nb == 0:
                continue

            # end of meta
            if line == '---':
                inside_meta = False
                continue

            if inside_meta:
                meta.append(line)
            else:
                # prevent appending empty lines following the meta header
                if new_lines or not (not line and not new_lines):
                    new_lines.append(line)

        self.markdown.meta = yaml.load('\r'.join(meta))

        return new_lines


class MetaExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add("yaml-meta", MetaPreprocessor(md), '>normalize_whitespace')


def makeExtension(*args, **kwargs):
    return MetaExtension(*args, **kwargs)
