import io
import pexpect
from . import parser


def render(document_contents):
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
        if not section.is_visible:
            result.write(section_content)
            continue

        # For now, ignore sections that aren't Python.
        code = section.code
        if code.language is not None and code.language != 'python':
            result.write(section_content)
            continue

        # Restart our Python process when we see a "restart" tag.
        if section.tag == 'restart':
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


def test(contents):
    # TODO: Implement this function. It should run the tests in the docs.
    pass


ARROWS = '>>> '
DOTS = '... '

class _PythonProcess:
    def __init__(self):
        self.process = None

    def restart(self):
        if self.process is not None:
            self.process.terminate(force=True)
            self.process = None

    def run(self, python_source_code):
        if self.process is None:
            self.process = pexpect.spawn('python', encoding='utf-8')
            self.process.logfile_read = io.StringIO()
            self.process.expect('>>> ')
            self.flush()

        if python_source_code.startswith('>>> '):
            return self.simulate(python_source_code)
        else:
            self.batch(python_source_code)

    def batch(self, python_source_code):
        self.sendline('try:', DOTS)
        self.sendline('    exec(', DOTS)

        for line in python_source_code.splitlines():
            self.sendline('        ' + repr(line + '\n'), DOTS)

        self.sendline('    )', DOTS)
        self.sendline('    print("ok")', DOTS)

        self.sendline('except Exception:', DOTS)
        self.sendline('    import traceback')
        self.sendline('    traceback.print_exc()', DOTS)
        self.sendline('    print("error")', DOTS)
        self.sendline('', ARROWS)

        result = self.flush()
        status = result.rsplit('\n', 1)[-1].strip()
        assert status in ['ok', 'error']

        if status != 'ok':
            raise Exception('Failed to execute section.\n' + result)

    def simulate(self, python_source_code):
        lines = list(python_source_code.splitlines())
        pairs = []
        for line in python_source_code.splitlines():
            if not line.strip():
                continue
            assert line.startswith((ARROWS, DOTS))
            expect, line = line[:4], line[4:]
            if pairs:
                pairs[-1].append(expect)
            pairs.append([line])
        pairs[-1].append(ARROWS)

        for line, expect in pairs:
            self.sendline(line, expect)

        result = self.flush()
        return result.replace('\n>>> ', '\n\n>>> ') + '\n'

    def sendline(self, line, expect=[ARROWS, DOTS]):
        self.process.sendline(line)
        self.process.expect(expect)

    def flush(self):
        value = self.process.logfile_read.getvalue().replace('\r\n', '\n')
        assert value and '\n' in value
        result, remainder = value.rsplit('\n', 1)
        self.process.logfile_read = io.StringIO()
        self.process.logfile_read.write(remainder)
        return result
