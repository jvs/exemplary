from . import parser


def test_document(document_contents):
    glob_env, local_env = {}, {}

    for section in parser.parse_document(document_contents):
        if isinstance(section, str):
            continue

        # For now, ignore sections that aren't Python.
        code = section.code
        if code.language is not None and code.language != 'python':
            continue

        # Ignore examples with the "skip example" tag.
        if section.tag == 'skip example':
            continue

        # Reset our environment when we see a "fresh example" tag.
        if section.tag == 'fresh example':
            glob_env, local_env = {}, {}

        # Ignore sections that use the repl.
        if code.body.strip().startswith('>>> '):
            continue


        print(f'# Testing Python section on line {code._position_info.start.line}:')
        print(make_preview(code.body))
        try:
            exec(code.body, glob_env, local_env)
        except Exception:
            print('# This section failed:')
            print(code.body)
            raise


def make_preview(python_source_code):
    preview = []
    for line in python_source_code.splitlines():
        if not line.strip() or 'import' in line:
            continue
        preview.append(line)
        if len(preview) > 6:
            break
    return '\n'.join(preview)
