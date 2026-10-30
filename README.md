# py2mlog
A python to mindustry logic (mlog) compiler.
## Install
To install py2mlog, run:
```sh
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
`while` loops, `break` and `continue`:
```py
while True:
    if y > 0:
        y -= 1
        continue

    if x > 10:
        break

    x += 1
```
`assert` statements for some reason:
```py
assert False, "Oopsie!"
```
Non-recursive custom function definitions.
> **Note**: these functions **do not** use a call stack.
```py
def is_odd(n):
    return n % 2 == 1


sixty_seven_is_odd = is_odd(67)
```

## Things to note
**Do not** use any variable prefixed with `__p2m`; they are reserved for the compiler.

## AI assistance
Some testcases in `tests/` were generated using AI tools and reviewed/rewritten by me.
Any code from me in the rest of the repository was manually handwritten.

## Credits
[pyndustric](https://github.com/Lonami/pyndustric) was the main inspiration for this project. It's really cool, you should check it out!

## Contributing
All contributions are more than welcome!
More information can be found in [CONTRIBUTING.md](CONTRIBUTING.md).
