"""This extensions adds a summary support to markdown.

A summary is a markdown paragraph that will be extracted from the markup text
and stored in a summary attribute of the markdown object.

A summary is defined with a [summary] tag:

```markdown
    [summary]
    This is the summary paragraph.

    And this is the rest of the file.
```

The summary paragraph will be removed from the final html text.

If no summary tag is set, the first paragraph will be extracted and the text
inside will be used as a summary.
"""

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


__all__ = ['SummaryExtension']


class SummaryPreprocessor(Preprocessor):
    """This processors will extract the [summary] tagged paragraph if existing
    and store its content in a *summary* attribute of the markdown instance.
    """
    def run(self, lines):
        inside_summary = False
        new_lines = []
        summary = []

        for line in lines:
            if line.strip() == '[summary]':
                inside_summary = True
                continue
            elif inside_summary and not line.strip():
                inside_summary = False
                continue

            if inside_summary:
                summary.append(line)
            else:
                new_lines.append(line)

        if summary:
            self.markdown.summary = '\r'.join(summary)
        else:
            self.markdown.summary = None

        return new_lines


class SummaryTreeProcessor(Treeprocessor):
    """If the *summary* of markdown instance is not set, extracts the first
    paragraph of the tree and uses its text as the summary.
    """
    def run(self, root):
        if not hasattr(self.markdown, 'summary'):
            self.markdown.summary = None

        if self.markdown.summary is not None:
            return root

        p = root.find('p')

        if p is not None:
            self.markdown.summary = ''.join(p.itertext())

        return root


class SummaryExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('summary', SummaryPreprocessor(md), '_end')
        md.treeprocessors.add('summary', SummaryTreeProcessor(md), '_end')


def makeExtension(**kwargs):
    return SummaryExtension(**kwargs)
