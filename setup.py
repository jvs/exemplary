import re
import setuptools


def long_description():
    with open('README.md') as f:
        return f.read()


def install_requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def version():
    with open('exemplary/__init__.py') as f:
        regex = re.compile('\\n__version__\\s*=\\s*[\'"]([\\d\\.]+)[\'"]\n')
        return regex.search(f.read()).group(1)


setuptools.setup(
    name='exemplary',
    version=version(),
    author='jvs',
    author_email='vonseg@protonmail.com',
    url='https://github.com/jvs/exemplary',
    description='Build and test your Python examples',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    install_requires=install_requires(),
    packages=['exemplary'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    platforms='any',
    license='MIT License',
    keywords=['documentation', 'examples'],
)
