from sourcer import Grammar


grammar = Grammar(r'''
    start = List(Text | VisibleSection | HiddenSection)

    Text = (ExpectNot(Marker) >> /.|\n/)+
        |> `lambda x: ''.join(x)`

    Marker = "```" | "~~~" | "<!--"

    class VisibleSection {
        is_visible: `True`
        tag: Opt(InlineTag) << /[\s\n]*/
        code: Code
    }

    class HiddenSection {
        is_visible: `False`
        tag: StartComment >> DanglingTag
        code: Code << /(\s|\n)*\-\->/
    }

    InlineTag = StartComment >> /.*?(?=\s*\-\->)/ << /\s*\-\-\>/
        |> `lambda x: x.lower() or None`

    DanglingTag = (/[^\n]*/ << /(\s|\n)*/)
        |> `lambda x: x.strip().lower() or None`

    HiddenBody = /(.|\n)*?(?=\s*\-\-\>)/

    StartComment = /\<\!\-\-[ \t]*/

    Code = CodeSection("```") | CodeSection("~~~")

    class CodeSection(marker) {
        open: marker
        language: /[^\n]*/ |> `lambda x: x.strip().lower() or None` << /\n/
        body: List(ExpectNot(marker) >> /.|\n/) |> `lambda x: ''.join(x)`
        close: marker
    }
''')


def parse_document(document_contents):
    return grammar.parse(document_contents)
