from textwrap import dedent
import pytest

import exemplary


def test_simple_rendering():
    result = exemplary.interpreter.render_document(dedent(r'''
        ```python
        greeting = "hello"
        friend = "world"
        ```

        ```python
        >>> print(f"{greeting}, {friend}.")
        ```
    '''))

    assert result == dedent(r'''
        ```python
        greeting = "hello"
        friend = "world"
        ```

        ```python
        >>> print(f"{greeting}, {friend}.")
        hello, world.
        ```
    ''')

    result = exemplary.interpreter.render_document(dedent(r'''
        ```python
        >>> from collections import defaultdict
        >>> d = defaultdict(list)
        >>> d['foo'].append('bar')
        >>> d['foo']
        >>> d['baz']
        ```
    '''))
    assert result == dedent(r'''
        ```python
        >>> from collections import defaultdict
        >>> d = defaultdict(list)
        >>> d['foo'].append('bar')
        >>> d['foo']
        ['bar']

        >>> d['baz']
        []
        ```
    ''')

    # Make sure we can render the document multiple times.
    result2 = exemplary.interpreter.render_document(result)
    assert result2 == result


def test_the_test_function():
    exemplary.interpreter.test_document(dedent(r'''
        ```python
        result = True
        ```

        ```bash
        printenv
        ```

        <!--
        ```python
        assert result
        ```
        -->

        <!-- skip example -->
        ```python
        assert False
        ```
    '''))

    with pytest.raises(AssertionError):
        exemplary.interpreter.test_document(dedent(r'''
            ```python
            result = False
            ```

            <!--
            ```python
            assert result
            ```
            -->
        '''))


def test_parsing_simple_example():
    g = exemplary.parser
    result = g.parse(dedent(r'''
        # foo
        bar
        <!-- baz -->
        ```fiz
        buz zim
        ```
        zam
    '''))
    assert result == [
        '\n# foo\nbar\n',
        g.VisibleSection(
            is_visible=True,
            tag='baz',
            code=g.CodeSection(
                open='```',
                language='fiz',
                body='buz zim\n',
                close='```',
            ),
        ),
        '\nzam\n',
    ]


def test_parsing_different_kinds_of_section():
    result = exemplary.parser.parse(dedent(r'''
        # tilde, tag, language
        <!-- fiz -->
        ~~~buz
        ```zim```
        ~~~

        # tilde, no tag, language
        ~~~fiz
        buz ```zim```
        ~~~

        # tilde, tag, no language
        <!-- fiz -->
        ~~~
        buz ~~zim~~
        ~~~

        # tilde, no tag, no language
        ~~~
        buz ```~~zim~~```
        ~~~

        # backtick, tag, language
        <!-- fiz -->
        ```buz
        ~~~zim~~~
        ```

        # backtick, no tag, language
        ```fiz
        buz ~~~zim~~~
        ```

        # backtick, tag, no language
        <!-- fiz -->
        ```
        buz ~~zim~~
        ```

        # backtick, no tag, no language
        ```
        buz ~~~``zim``~~~
        ```

        # hidden, tag, language
        <!-- fiz
        ```buz
        zim
        ```
        -->

        # hidden, no tag, language
        <!--
        ```fiz
        buz <!-- zim
        ```
        -->

        # hidden, tag, no language
        <!-- fiz
        ~~~
        buz ~~zim~~
        ~~~
        -->

        # hidden, no tag, no language
        <!--
        ~~~
        buz ```~~zim~~```
        ~~~
        -->
    '''))

    sections = [x for x in result if not isinstance(x, str)]
    assert len(sections) == 12

    expect_tags = ['fiz', None] * 6
    expect_langs = ['buz', 'fiz', None, None] * 3

    tags = [x.tag for x in sections]
    langs = [x.code.language for x in sections]

    assert tags == expect_tags
    assert langs == expect_langs
