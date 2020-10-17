# Exemplary

A micro library for testing the Python examples in your documentation.


## Installation

```console
pip install exemplary
```

Exemplary requires Python 3.6 or later.


## What problem does Exemplary solve?

Exemplary solves two main problems:

* It makes sure that the examples in your documentation actually work.
* It renders the output for your examples, so that your documentation shows
  what your users are really going to see.


## How do you use Exemplary?

### For testing:

Put some Python sections in your markdown files.

Then, in your tests:

```python
import glob
import exemplary

def test_docs():
    # Run all the examples in your markdown files:
    exemplary.run(glob.glob('**/*.md'))
```

This raises an exception if any of your examples fail.


### For rendering:

In this context, "rendering" means, "Taking an example and showing what it looks
like when you run it in Python's interactive interpreter."

So, let's say you have some markdown like this:

~~~markdown
# How to use deque

```python
>>> from collections import deque
>>> d = deque([1, 2, 3])
>>> d.popleft()
>>> d.pop()
```
~~~

In your build script, run exemplary with `render=True`:

```python
import glob
import exemplary

def render_docs():
    # Render all the examples in your markdown files:
    exemplary.run(glob.glob('**/*.md'), render=True)
```

Aftwards, the example would look like this:

~~~markdown
# How to use deque

```python
>>> from collections import deque
>>> d = deque([1, 2, 3])
>>> d.popleft()
1

>>> d.pop()
3
```
~~~

Exemplary runs these kinds of examples in Python's interactive interpreter, and
adds the output to your examples. (Note that Exemplary adds an extra newline
after the interpreter's output, to improve readability.)

If you run Exemplary again, it will render the example again, ignoring any
output that may already appear in the example. So you can run exemplary multiple
times as you edit your documentation.

Note: Because Exemplary modifies your files, make sure they are committed to
git before rendering them.


## What if I have multiple examples in one markdown file?

For each file, Exemplary essentially runs each example in the same interpreter.
This allows you to break up your examples with text sections.

If you need an example to start fresh in its own namespace, you can put a special
HTML comment in the line before your example:

~~~markdown
&lt;!-- fresh example --&gt;
```python
import foo
...
```
~~~

When Exemplary sees the "fresh example" comment, it essentially restarts the
interpreter that it's using to test and render your examples.


## How can I hide some of the tests for my examples?

Exemplary looks for code sections even in HTML comments. This lets you write
additional tests for your examples (to make sure they really work), without
cluttering up your documentation.

For example:
~~~markdown

# Some Example

Setup:

```python
import something
foo = do_something()
```

&lt;!--
```python
assert foo.some_property
assert some_other_predicate(foo)
```
--&gt;
~~~

Exemplary will run both Python sections -- the one before the comment and the
one inside the comment.

This way you can:

* thoroughly test your examples
* keep examples and tests together in the same file
* hide the tests so that they don't detract from the documentation

Taken to the extreme, you could view all of your unit tests as part of your
documentation, and structure them this way.


## What if I don't want Exemplary to test an example?

Put the HTML comment `&lt;!-- skip example --&gt;` on the line above each
example that you want Exemplary to ignore.
