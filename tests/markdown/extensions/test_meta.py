from unittest.mock import Mock

from pblog.markdown.extensions import meta


class TestMetaPreprocessor:
    def test_sets_meta_to_none_if_no_meta(self):
        preproc = meta.MetaPreprocessor()
        preproc.markdown = Mock()

        preproc.run(['A paragraph'])

        assert preproc.markdown.meta is None

    def test_extracts_meta(self):
        preproc = meta.MetaPreprocessor()
        preproc.markdown = Mock

        preproc.run(['---', 'foo: bar', 'bar:', '    - baz', '---'])

        assert preproc.markdown.meta == {'foo': 'bar', 'bar': ['baz']}

    def test_removes_meta(self):
        preproc = meta.MetaPreprocessor()
        preproc.markdown = Mock()

        lines = preproc.run(['---', 'foo: bar', '---', '', 'Paragraph'])

        assert lines == ['Paragraph']
