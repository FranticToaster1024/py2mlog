# py2mlog
A python to mindustry logic (mlog) compiler. https://xkcd.com/927/

## Website
Don't want to deal with all the annoying cli stuff? Try py2mlog out in your browser, at https://frantictoaster1024.github.io/py2mlog/.

## Install
Since it's a CLI tool, you can use `pipx` or `uv` or something to install it. It's probably the better method, if available. Unless you plan to use the modules in your python file for some reason?

Or just install it with regular pip:
```sh
# create and activate a venv
# i guess you could skip this if you wanted to
python -m venv .venv
.venv/Scripts/activate.bat  # or however you activate a venv in your shell

pip install "git+https://github.com/FranticToaster1024/py2mlog.git"
```

## Usage
Basic usage:
```sh
py2mlog path/to/your/file.py
```
The output file will be `path/to/your/file.mlog` by default.

You can also compile all .py files in a folder:
```sh
py2mlog path/to/src/
```

You can compile multiple files at once by passing them as space-separated arguments, like so:
```sh
py2mlog path/to/your/file.py path/to/your/other/file.py path/to/third/file.py
```

Same with folders:
```sh
py2mlog path/to/dir/ path/to/other/dir/ path/to/third/dir/
```

You can even mix files and folders:
```sh
py2mlog path/to/your/file.py path/to/your/other/file.py path/to/dir/
```

Additionally, you can override output files and folders by listing them as space-separated arguments after `-o` or `--output`. These output paths correspond to the input paths in order, and if there are fewer output paths than input paths, input paths without an output path specified will use the default. For example:
```sh
py2mlog path/to/dir/ path/to/file.py path/to/other/file.py -o path/to/mlog/dir/ file.mlog 
```

In the above example:
- `path/to/dir/` will compile to `path/to/mlog/dir/`,
- `path/to/file.py` will compile to `file.mlog`,
- and `path/to/other/file.py` will compile to `path/to/other/file.mlog`.

You can use `-s` or `--stdout` to print the compiled mlog to stdout. This does not override or clash with the file output.

You can use `--no-file` to disable the file output. This must be used with `-s` or `--stdout`, otherwise the compiled program has nowhere to go.

Information, warnings, and other diagnostics are printed to stderr.

## Supported features
Assignment and operators:
```py
x = 42
y = x**2
y -= 6.7
z = x < y > (4.2 if x < 123 else 6.7)
```

`If`, `elif` and `else`:
```py
if foo < 67:
    x += 10
elif foo < 100:
    x -= 20
else:
    x *= 2
```

`while` loops, `break`, `continue` and loop/else:
```py
while True:
    if y > 0:
        y -= 1
        continue

    if x > 10:
        break

    x += 1
else:
    completed = True
```

`for ... range()`:
```py
result = 0
for i in range(5):
    for j in range(i, 10 * 2, 3):
        result += j
```

`assert` statements for some reason:
```py
assert False, "Oopsie!"
```

Very basic python builtins (`print` not supported yet), more coming soon<sup>TM</sup>.
```py
x = abs(-5)
y = ord("!")
z = max(a, b)  # only 2 args for now unfortunately
```

Non-recursive custom function definitions.
> **Note**: these functions **do not** use a call stack.
```py
def is_odd(n):
    return n % 2 == 1


sixty_seven_is_odd = is_odd(67)
```

Non-recursive custom inline function definitions using the `@inline` decorator:
```py
@inline
def func(x):
    return x * 2 + 1


y = func(42)
```
<!--these work quite beautifully but i have no idea why it works atp-->

**Recursive functions are unsupported!** There is a very basic check in place, but it probably doesn't cover all cases.


Imports from `py2mlog_api`, which don't actually do anything except please your type checker.
```py
from py2mlog_api import Env, Links
```
The `py2mlog_ai.pyi` type stub still needs much work though for the type checker to stop complaining.

Access to some mlog builtins via `Env.*`, just like pyndustric.
```py
c = Env.copper
w = Env.water
```

Links (`Links` makes more sense imo but `Link` is supported for compatibility with pyndustric):
```py
l = Link[0]
l = Links[0]
```

Color literals (through either the `Color()` builtin or a string literal in the form "%ffffff" for compatibility with pyndustric):
```py
red = "%FF0000"
green = Color("%00FF00")
green = Color("00FF00")
green_with_alpha = Color("00FF00FF")
blue = Color(0x0000FF)
```

All draw operations, through the `Screen.*` namespace. If I didn't mess up somewhere, these should be fully compatible with pyndustric. I'm too lazy to write an actual sample so here is a snippet from the tests:
```py
Screen.clear(0, 127, 255)
Screen.fill(a, b, c)  # alias for 'Screen.clear()'
Screen.color(a, b, c)  # default alpha is 255
Screen.color(a, b, c, d)
Screen.col(Color("%ffffff"))
Screen.stroke(3)
Screen.line(0, 0, x2=80, y2=160)
Screen.rect(0, 0, 80, height=160)
Screen.fill_rect(a, y=b, width=c, height=d)  # alias for 'Screen.rect'
Screen.linerect(0, 0, 80, 160)
Screen.poly(80, 80, 6, 40, 0)
Screen.line_poly(80, 80, 6, 40, 0)

Screen.flush()  # default is 'display1'
```


TODO: Unit.*


## Things to note
**Do not** use any variable prefixed with `__p2m`; they are reserved for the compiler.
Error messages can sometimes be inaccurate or misleading. I should probably make more specific error types. The compiler does not currently check and enforce the mlog 1000 line limit.

## Future goals/To-do list
- **Better errors**
- Optimization
- Inline mlog
- Config file?
- CLI upgrade?
- Passing functions (representing functions as numbers instead of labels)
- Recursive functions (stack frames)

## AI assistance
Some testcases in `tests/` were generated using AI tools and reviewed/rewritten by me.
Additionally, AI assistance was used for configuration files (such as .github/workflows/ci.yml, pyproject.toml).
AI assistance was also used in some parts of the source code, including [`func_utils.py`](src/py2mlog/compiler/func_utils.py) and [`script.js`](web/script.js). All source code was handwritten though.

## Credits
[mimex-data](https://github.com/cardillan/mimex-data) is the main source of data for stuff like mlog builtins, included in this repo as a submodule. I probably messed up here considering it has no license, so hey uh Cardillan if you want me to get rid of this I'm so sorry and feel free to let me know.

[pyodide](https://github.com/pyodide/pyodide) is used to run the py2mlog python package in a browser.

[pyndustric](https://codeberg.org/Lonami/pyndustric) was the main inspiration for this project. It's really cool, you should check it out!
[minpiler](https://github.com/neumond/minpiler) is also really cool!

Also, thank you to all contributors, users, and members of the mindustry community for your guidance and support!

## Contributing
All contributions are more than welcome!
More information can be found in [CONTRIBUTING.md](CONTRIBUTING.md).
