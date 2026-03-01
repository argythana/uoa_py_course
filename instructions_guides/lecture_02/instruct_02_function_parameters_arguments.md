## Parameters and arguments: keyword, positional, optional, required, and Combinations

Remember: "variables" in Python are: a "name" which refers to an object and is always a "name = value" pair.
Remember: such a "name" is a "reference" to an object and has always a "type", which means that it has some special characteristics, attributes, "properties" and "methods".

Parameters: the names that appear in a function definition.
Argument: the values that a function uses as input to return as result as output.

[What is an argument](https://docs.python.org/3/glossary.html#term-argument)
    > Argument is a value passed to a function (or method) when calling the function.

[What is a Parameter](https://docs.python.org/3/glossary.html#term-parameter) is a named entity that specifies what argument a function may accept.

[Difference between Parameters and Arguments:](https://docs.python.org/3/faq/programming.html#what-is-the-difference-between-arguments-and-parameters)

Parameters are defined by the names that appear in a function definition.
Parameters define what types of arguments a function can accept.
Arguments are the values actually passed to a function when calling it.

Remember: Parameters are "names" (and in best practice also "types") in the function definition.
Arguments are "values" in the function call.

In short:
* Parameters = "names" (and "type") used in definition.
* Arguments = "values" used in call.

There are [five types of parameters](https://docs.python.org/3/glossary.html#term-parameter):
* positional-or-keyword: positional argument or keyword argument.
* positional-only: positional argument only.
* keyword-only: keyword argument only.
* var-positional: variable positional argument.
* var-keyword: variable keyword argument.

There are [two types of arguments](https://docs.python.org/3/glossary.html#term-argument):
* keyword.
* positional.

[What is an argument](https://docs.python.org/3/glossary.html#term-argument) is a value passed to a function when calling the function:
> keyword => referenced by the name, assign value to a name.
> positional => referenced by position.

> Argument is a value passed to a function (or method) when calling the function.
> There are two kinds of arguments:

> keyword argument: an argument preceded by an identifier (e.g. name=) in a function call or passed as a value in a dictionary preceded by **.
> For example, 3 and 5 are both keyword arguments in the following calls to complex():

```python
complex(real=3, imag=5)
complex(**{'real': 3, 'imag': 5})
```

> Positional argument: an argument that is not a keyword argument.
> Positional arguments can appear at the beginning of an argument list and/or be passed as elements of an iterable preceded by *.
> For example, 3 and 5 are both positional arguments in the following calls:

```python
complex(3, 5)
complex(*(3, 5))
```

Depending on the function definition, the arguments can be:
* optional.
* required.

### Required arguments
Required arguments are arguments that must be passed to the function in the function call.

### Optional arguments
Optional arguments are arguments that have a default value in the function definition.
In the function call, the argument reference is optional, because the default value is used if a different value is not provided.
Assigning a default value for the parameter in the function definition => The argument reference is optional when calling the function.

### Positional arguments
Positional argument: Neither default value, not default name, no name at all.
Optional value assignment at definition, necessary value assignment when calling the function.
When calling a function you have to assign values for the positional arguments before the keyword arguments (else => SyntaxError).
TypeError: missing required positional argument.

Assigning a default value for the parameter in the function definition => The argument reference is optional when calling the function.
Optional arguments are arguments that have a default value.
Positional arguments: Neither default value, not default name, no name at all.
Optional value assignment at definition, necessary value assignment when calling the function.

**When calling a function you have to assign values for the positional arguments before the keyword arguments**
(else => SyntaxError).
`TypeError: missing required positional argument.`

```python
def example_function(a, b, c):
    print(a, b, c)

# Correct usage
example_function(1, 2, 3)  # All positional arguments
example_function(a=1, b=2, c=3)  # All keyword arguments
example_function(1, b=2, c=3)  # Positional arguments before keyword arguments

# Incorrect usage
example_function(a=1, 2, 3)  # SyntaxError: positional argument follows keyword argument
```

Must Read: [Positional, Keyword, optional, required:](https://stackoverflow.com/a/57819001)
Oftenly: The accepted answer is not always the most useful answer in stackoverflow.
In this case the two top answers are both useful.
> Notice: check dates, check versions. google search is not a simple skill.

Python docs, [since python 3.8 we may also use positional only parameters](https://docs.python.org/3.8/whatsnew/3.8.html#positional-only-parameters).
In my humble opinion, this is one great "new" feature of Python.
positional-only:
specifies an argument that can be supplied only by position.
Positional-only parameters can be defined by including a / character in the parameter list of the function definition after them.
for example `posonly1` and `posonly2` in the following:

```python
def func(posonly1, posonly2, /, positional_or_keyword): ...
```

### Important:
Identify which arguments are:
positional, keyword, optional, required,
for the print() function.

```python
help(print)
```
```
Help on built-in function print in module builtins:

print(...)
    print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

    Prints the values to a stream, or to sys.stdout by default.
    Optional keyword arguments:
    file:  a file-like object (stream); defaults to the current sys.stdout.
    sep:   string inserted between values, default a space.
    end:   string appended after the last value, default a newline.
    flush: whether to forcibly flush the stream.
```

### More Reading:
* [var-positional](https://docs.python.org/3/glossary.html#term-parameter)
    > an arbitrary sequence of positional arguments can be provided,
  > (in addition to any positional arguments already accepted by other parameters.

* [var-keyword](https://docs.python.org/3/glossary.html#term-parameter)
    > arbitrarily many keyword arguments can be provided
    > (in addition to any keyword arguments already accepted by other parameters).
