import argparse
import glob


def main():
    argparser = argparse.ArgumentParser(
        description='Test and render Python examples.')
    argparser.add_argument('--paths', nargs='+', required=True,
        help='The files to process, may be a glob pattern.')
    argparser.add_argument('--render', action='store_true',
        help='Render the files, in addition to testing them.')

    args = argparser.parse_args()
    pathnames = []
    for path in args.paths:
        pathnames.extend(glob.glob(path, recursive=True))
    run(pathnames, render=args.render)


if __name__ == '__main__':
    main()
