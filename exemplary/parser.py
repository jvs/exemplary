from sourcer import Grammar


grammar = Grammar(r'''
    `from textwrap import dedent`

    start = List(Text | VisibleSection | HiddenSection)

    Text = (ExpectNot(Marker) >> /.|\n/)+
        |> `lambda x: ''.join(x)`

    Marker = "```" | "~~~" | "<!--" | "-->"

    class VisibleSection {
        tag: Opt(InlineTag) << /[\s\n]*/
        body: Code
    }

    class HiddenSection {
        tag: StartComment >> DanglingTag
        body: Code << /(\s|\n)*\-\->/
    }

    InlineTag = StartComment >> /.*?(?=\s*\-\->)/ << /\s*\-\-\>/
        |> `lambda x: x or None`

    DanglingTag = (/[^\n]*/ << /(\s|\n)*/)
        |> `lambda x: x.strip() or None`

    HiddenBody = /(.|\n)*?(?=\s*\-\-\>)/ |> `dedent`

    StartComment = /\<\!\-\-[ \t]*/

    Code = CodeSection("```") | CodeSection("~~~")

    class CodeSection(marker) {
        open: marker
        language: /[^\n]*/ |> `lambda x: x.strip() or None` << /\n/
        body: List(ExpectNot(marker) >> /.|\n/) |> `lambda x: dedent(''.join(x))`
        close: marker
    }
''')


def parse(text):
    return grammar.parse(text)
