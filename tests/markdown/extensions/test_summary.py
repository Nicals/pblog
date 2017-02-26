from unittest.mock import Mock
import xml.etree.ElementTree as ElementTree

from pblog.markdown.extensions import summary


class TestSummaryPreprocessor:
    def test_removes_summary(self):
        preproc = summary.SummaryPreprocessor()
        preproc.markdown = Mock()

        lines = preproc.run(['foo', '', ' [summary] ', 'hello', '', 'bar'])

        assert lines == ['foo', '', 'bar']

    def test_sets_md_summary_to_none_if_no_tag(self):
        preproc = summary.SummaryPreprocessor()
        preproc.markdown = Mock()

        preproc.run(['foo', 'bar', '', 'baz'])

        assert preproc.markdown.summary is None

    def test_sets_md_summary_attribute(self):
        preproc = summary.SummaryPreprocessor()
        preproc.markdown = Mock()

        preproc.run(['foo', '', ' [summary] ', 'hello', '', 'bar'])

        assert preproc.markdown.summary == 'hello'


class TestSummaryTreeProcessor:
    def test_keeps_summary_if_already_set(self):
        treeproc = summary.SummaryTreeProcessor()
        treeproc.markdown = Mock(summary='foo')

        treeproc.run(ElementTree.fromstring('<html><p>Foo</p><p>Bar</p></html>'))

        assert treeproc.markdown.summary == 'foo'

    def test_uses_first_paragraph_if_no_summary(self):
        treeproc = summary.SummaryTreeProcessor()
        treeproc.markdown = Mock(summary=None)

        treeproc.run(ElementTree.fromstring('<html><p>Ham <a href="#">spam</a></p><p>Bar</p></html>'))

        assert treeproc.markdown.summary == 'Ham spam'

    def test_no_paragraph(self):
        treeproc = summary.SummaryTreeProcessor()
        treeproc.markdown = Mock(summary=None)

        treeproc.run(ElementTree.fromstring('<html><img src="Foo" /></html>'))

        assert treeproc.markdown.summary is None
