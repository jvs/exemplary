from . import renderer
from . import tester


def run(pathnames, render=False):
    for pathname in pathnames:
        with open(pathname) as f:
            contents = f.read()

        print('# Testing', pathname)
        tester.test_document(contents)

        if render:
            print('# Rendering', pathname)
            rendering = renderer.render_document(contents)

            with open(pathname, 'w') as f:
                f.write(contents)

        print()
