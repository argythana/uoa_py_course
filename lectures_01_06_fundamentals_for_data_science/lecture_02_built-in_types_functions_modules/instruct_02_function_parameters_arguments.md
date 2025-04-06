# Function Parameters and Arguments: keyword, positional, optional, required, and combinations

Remember: "variables" in Python are: a "name" which refers to an object and is always a "name = value" pair.   
Remember: such a "name" is a "reference" to an object and has always a "type", which means that it has some special characteristics, attributes, "properties" and "methods".

## 1. The difference between `parameters` and `arguments`

`Parameters`: the names that appear in a function definition.    
`Arguments`: the values that a function uses as input, then does something and then "returns" an output.    


[What is a Parameter](https://docs.python.org/3/glossary.html#term-parameter)   
> Parameters is a named entity that specifies what argument a function may accept. 

[What is an argument](https://docs.python.org/3/glossary.html#term-argument)   
> Argument is a value passed to a function (or method) when calling the function.   

[Difference between Parameters and Arguments:](https://docs.python.org/3/faq/programming.html#what-is-the-difference-between-arguments-and-parameters)   

Parameters are defined by the names that appear in a function definition.     
Parameters define what types of arguments a function can accept.  
Arguments are the values actually **passed** to a function when calling it.    

**Summary:**     
`Parameters` are "names" defined in the function definition.   
`Arguments` are "values" provided in the function call.  

**Shorter Summary:**    
* `Parameters` = "names" in definition.
* `Arguments` = "values" in call.

**Shortest Summary:**  
* `Parameters` = "names".
* `Arguments` = "values".


## 2. The difference between the concepts of `positional` and `keyword` 

There are [five types of parameters.](https://docs.python.org/3/glossary.html#term-parameter) 

The different types of parameters accept different types of arguments, shown in the table below:

| **Parameter type**       | **Accepted Argument type**              |
|--------------------------|-----------------------------------------|
| **positional-or-keyword**| Positional argument or keyword argument |
| **positional-only**      | Positional argument only                |
| **keyword-only**         | Keyword argument only                   |
| **var-positional**       | Variable positional argument            |
| **var-keyword**          | Variable keyword argument               |

There are [two types of arguments.](https://docs.python.org/3/glossary.html#term-argument)  
* `keyword`  (or 'var-keyword').
* `positional` (or 'var-positional').

Focus on the difference between `keyword` and `positional` arguments.  

### `keyword` arguments
> An argument preceded by an identifier (e.g. name=) in the function call.   
> Referenced by the corresponding parameter name, and a value is assigned to that name.  


For example, 2 and 5 are both keyword arguments in the following calls to pow():
    
```python
# 2 to the power of 5. Using keyword arguments for base (βάση) and exponent (εκθέτης).
pow(base=2, exp=5)
Out[11]: 32
```

### `positional` arguments
> An argument that is not a keyword argument.  
> Referenced by its position in the function call, not by its name.    
> No argument name in function call, just the "value".  
> The value is assigned to the corresponding parameter by its position.  

Example:

```python
# 2 to the power of 5. Using positional arguments.
pow(2, 5)
Out[11]: 32
```

> The order of positional arguments in the function call is important, must match the order of the parameters in the function definition.

Think that:  
* the parameters in the definition is a like a list of names, and 
* the values in the "call" is a like list of values that correspond to the names in the definition.  

Since positional arguments do not have a name, you need to "pass them" to the function in the correct order.  
This should be obvious, but is not always the case.  
For example,

```python
# 2 to the power of 5
pow(2, 5)
Out[5]: 32

# 5 to the power of 2
pow(5, 2)
Out[6]: 25

# 2 to the power of 4
pow(2, 4)
Out[7]: 16

# 4 to the power of 2
pow(4, 2)
Out[8]: 16
```

**Important:**
Assign values for positional arguments first before passing values to keyword arguments.  
Python does not allow you to pass a positional argument after a keyword argument.  
It is a way to avoid confusion and make the code more readable.  

Examples:  
The following code will raise a `SyntaxError`:

```python
# Using keyword argument before positional argument => SyntaxError
pow(base=2, 5)
  Cell In[13], line 1
    pow(base=2, 5)
                 ^
SyntaxError: positional argument follows keyword argument
```

The following code will raise a `TypeError`:  
```python
# no argument for base => TypeError missing required argument
pow(exp=5)
TypeError: pow() missing required argument 'base' (pos 1)
```

This will work:

```python
# 2 to the power of 5. Using positional argument for base and keyword for exponent.
pow(2, exp=5)
Out[15]: 32
```

**Summary:**
* `keyword` arguments are passed by name, and the order does not matter.
* `positional` arguments are passed by position, and the order matters.

**Shorter Summary:**
* `keyword` arguments are passed by name.
* `positional` arguments are passed by position.

**Shortest Summary:**
* `keyword`: name = value.
* `positional`: value.


## 3. The difference between the concepts `optional` and `required`.

Depending on the function definition, arguments can be:
* `optional`.
* `required`.

### `required` arguments
Required arguments are arguments that must always be passed to the function in the function call.  
There is no value set in the function definition, so a value must be passed in the function call.

### `optional` arguments
Optional arguments are arguments that have a "default value" set in the function definition.  
Therefore, they are not required to be used in the function call.
Optinally, you may pass a different value in the function call, but it is not required.
In the function call, if a different value is not provided, the default value is used.

Assigning a default value for the parameter in the function definition => The argument reference is optional when calling the function.  

Optional value assignment at definition, necessary value assignment when calling the function.  

Examples of wrong usage with missing required arguments:
```python
def example_function(a, b):
  """Simple function that takes two arguments and prints them."""
    print(a, b)

# Incorrect usage: missing the second required positional argument
example_function(1)
TypeError: example_function() missing 1 required positional argument: 'b'

# Incorrect usage: missing the first required positional argument
example_function(b=1)
TypeError: example_function() missing 1 required positional argument: 'a'
```

**Summary:**
* `optional`: argument value in function definition -> The argument is optional when calling the function.  
* `reuired`: No value in function definition -> necessary value passing when calling the function.    

**Shorter Summary:**
* `optional`: value in definition, optional different value in call.
* `required`: no value in definition, required value in call.  

**<mark>Homework reading on Parameters</mark>**  
[Examples of positional, keyword, optional, required Parameters](https://stackoverflow.com/a/57819001) 

The accepted answer is not always the most useful answer in Stackoverflow.   
Also check the date of each reply because things change.      
In this case the 2 top answers are both useful.   
> Conclusion: A parameter can be required or optional but not both at the same time.    
> A parameter can also be positional, keyword, or both at the same time.


## 4. Exercise to test your understanding:
Identify which parameters and which arguments are:   
`positional`, `keyword`, `optional`, `required`,
in the print() function.

Then ask an AI assistant to help you with the answer.

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

## 5. More advanced reading:

### Positional only parameters
[Since python 3.8 we have positional only parameters](https://docs.python.org/3.8/whatsnew/3.8.html#positional-only-parameters).     
In my humble opinion, this is one great "new" feature of Python.   

**Positional-only:**  
specifies an argument that can be supplied only by position.   
Positional-only parameters can be defined by including a / character in the parameter list of the function definition after them.  
for example `posonly1` and `posonly2` in the following:

**Var-positional:**
* [var-positional](https://docs.python.org/3/glossary.html#term-parameter)
    > an arbitrary sequence of positional arguments can be provided, 
  > (in addition to any positional arguments already accepted by other parameters.

**Var-keyword:**
* [var-keyword](https://docs.python.org/3/glossary.html#term-parameter)
    > arbitrarily many keyword arguments can be provided
    > (in addition to any keyword arguments already accepted by other parameters).
