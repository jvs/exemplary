from textwrap import dedent
from exemplary import parser


def test_parsing_simple_example():
    result = parser.parse(dedent(r'''
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
        parser.grammar.VisibleSection(
            is_visible=True,
            tag='baz',
            code=parser.grammar.CodeSection(
                open='```',
                language='fiz',
                body='buz zim\n',
                close='```',
            ),
        ),
        '\nzam\n',
    ]


def test_parsing_different_kinds_of_section():
    result = parser.parse(dedent(r'''
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
