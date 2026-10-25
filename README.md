# py2mlog
A python to mindustry logic (mlog) compiler.
# Install
To install py2mlog, run:
```sh
pip install "git+https://github.com/FranticToaster1024/py2mlog.git"
```
# Usage
Basic usage:
```sh
py2mlog path/to/your/file.py
```
The output file will be `path/to/your/file.mlog` by default.

You can compile multiple files at once by passing them as space-separated arguments, like so:
```sh
py2mlog path/to/your/file.py path/to/your/other/file.py path/to/third/file.py
```
Additionally, you can override output file(s) by listing them as space-separated arguments after `-o` or `--output`. These output files correspond to the input files in order, and if there are fewer output files than input files, input files without an output file specified will use the default, like so:
```sh
py2mlog path/to/file.py path/to/other/file.py -o first.mlog
```
In the above example, `path/to/file.py` will compile to `first.mlog` and `path/to/other/file.py` will compile to `path/to/other/file.mlog`.
# Supported features
Assignment and operators:
```py
x = 42
y = x ** 2
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
```
assert False, "Oopsie!"
```
Non-recursive custom function definitions.
> **Note**: these functions **do not** use a call stack.
```py
def is_odd(n):
    return n % 2 == 1

sixty_seven_is_odd = is_odd(67)
```
# Contributing
All contributions are more than welcome!
To install in editable mode:

```sh
git clone https://github.com/FranticToaster1024/py2mlog.git
cd py2mlog
```

From here, there are 2 methods:
- with hatch
    ```sh
    hatch shell
    ```
    Some useful commands:
    ```sh
    hatch check fmt
    hatch check code
    hatch run type-check
    hatch test
    ```

- without hatch
    ```sh
    python -m venv .venv
    .venv/Scripts/activate # or however you active a venv in your shell
    pip install -e ".[dev]"
    ```
    then
    ```sh
    ruff format .
    ruff check .
    pyright .
    pytest tests/
    ```

