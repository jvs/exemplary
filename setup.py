import setuptools


def long_description():
    try:
        with open('README.md') as f:
            return f.read()
    except:
        return ''


def install_requires():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setuptools.setup(
    name='exemplary',
    version='0.0.1',
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
