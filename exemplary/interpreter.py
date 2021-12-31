import io
import re
import sys

import pexpect

from . import parser


def run(pathnames, render=False):
    """
    Takes an iterable of pathnames to Markdown documents, then tests each one.

    If `render` is truthy, then this function also updates each document,
    filling in the output from Python's interactive interpreter.
    """
    print('\n# Running Exemplary...', flush=True)
    for pathname in pathnames:
        with open(pathname) as f:
            contents = f.read()

        print('# Testing', pathname, flush=True)
        test_document(contents)

        # Ignore documents that don't have any interactive-mode examples.
        if render and '\n>>> ' in contents:
            print('# Rendering', pathname, flush=True)
            rendering = render_document(contents)

            if rendering != contents:
                print('# Updating', pathname, flush=True)
                with open(pathname, 'w') as f:
                    f.write(rendering)


def test_document(document_contents):
    """
    Takes the contents of a Markdown document and executes each Python section.
    """
    global_env, local_env = {}, {}

    for section in parser.parse(document_contents):
        if isinstance(section, str):
            continue

        # For now, ignore sections that aren't Python.
        code = section.code
        if code.language != 'python':
            continue

        # Ignore examples with the "skip example" tag.
        if section.tag == 'skip example':
            continue

        # Reset our environment when we see a "fresh example" tag.
        if section.tag == 'fresh example':
            global_env, local_env = {}, {}

        # Ignore sections that use the repl.
        if code.body.strip().startswith('>>> '):
            continue

        print(f'# Testing Python section on line {code._position_info.start.line}:')
        print(_make_preview(code.body), flush=True)
        try:
            exec(code.body, global_env, local_env)
        except Exception:
            print('# This section failed:')
            print(code.body)
            raise
        print()


def render_document(document_contents):
    """
    Takes the contents of a Markdown document and executes each Python section.

    When it finds a Python section that begins with ">>>", it records the
    output from Python interpreter, and adds it to the section.

    Returns the contents of the Markdown document, where each interaction
    example includes the interpreter's output.
    """
    result = io.StringIO()
    proc = _PythonProcess()

    for section in parser.parse(document_contents):
        if isinstance(section, str):
            result.write(section)
            continue

        sec_info = section._position_info
        section_start, section_end = sec_info.start.index, sec_info.end.index
        section_content = document_contents[section_start : section_end + 1]

        # Ignore hidden sections when rendering the docs.
        if not section.is_visible or section.tag == 'skip example':
            result.write(section_content)
            continue

        # For now, ignore sections that aren't Python.
        code = section.code
        if code.language is not None and code.language != 'python':
            result.write(section_content)
            continue

        # Restart our Python process when we see a "fresh example" tag.
        if section.tag == 'fresh example':
            proc.restart()

        # Run the code.
        playback = proc.run(code.body)

        if playback is None:
            result.write(section_content)
        else:
            code_info = code._position_info
            code_start, code_end = code_info.start.index, code_info.end.index
            result.write(''.join([
                document_contents[section_start : code_start],
                code.open,
                code.language or '',
                '\n',
                playback,
                code.close,
                document_contents[code_end + 1 : section_end + 1],
            ]))

    proc.restart()
    return result.getvalue()


def _make_preview(python_source_code):
    preview = []
    for line in python_source_code.splitlines():
        if not line.strip() or 'import' in line:
            continue
        preview.append(line)
        if len(preview) > 6:
            preview.append('...')
            break
    return '\n'.join(preview)


class _PythonProcess:
    def __init__(self):
        self.process = None
        self._prompt_pattern = re.compile(r'(\>\>\>|\.\.\.) $')

    def restart(self):
        if self.process is not None:
            self.process.terminate(force=True)
            self.process = None

    def run(self, python_source_code):
        if self.process is None:
            self.process = pexpect.spawn(sys.executable, encoding='utf-8')
            self.process.logfile_read = io.StringIO()
            self.process.expect('>>> ')
            self.flush()

        if python_source_code.startswith('>>> '):
            return self.simulate(python_source_code)
        else:
            self.batch(python_source_code)

    def batch(self, python_source_code):
        self.sendline('try:')
        self.sendline('    exec(')

        for line in python_source_code.splitlines():
            self.sendline('        ' + repr(line + '\n'))

        self.sendline('    )')
        self.sendline('    print("ok")')
        self.sendline('except Exception:')
        self.sendline('    import traceback')
        self.sendline('    traceback.print_exc()')
        self.sendline('    print("error")')
        self.sendline('')

        result = self.flush()
        status = result.rsplit('\n', 1)[-1].strip()
        assert status in ['ok', 'error']

        if status != 'ok':
            raise Exception('Failed to execute section.\n' + result)

    def simulate(self, python_source_code):
        lines = list(python_source_code.splitlines())
        for line in python_source_code.splitlines():
            # Ignore lines that don't represent user input.
            if line.startswith(('>>>', '...')):
                self.sendline(line[4:])

        result = self.flush()
        return _add_padding(result)

    def sendline(self, line):
        self.process.sendline(line)
        self.process.expect(self._prompt_pattern)

    def flush(self):
        value = self.process.logfile_read.getvalue().replace('\r\n', '\n')
        assert value and '\n' in value
        result, remainder = value.rsplit('\n', 1)
        self.process.logfile_read = io.StringIO()
        self.process.logfile_read.write(remainder)
        return result


def _add_padding(contents):
    result = []
    was_prompt = True
    for line in contents.splitlines():
        if line.startswith('>>> ') and not was_prompt:
            result.append('')
        result.append(line.rstrip())
        was_prompt = line.startswith(('>>> ', '... '))
    result.append('')
    return '\n'.join(result)
