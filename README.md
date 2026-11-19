# py2mlog
A python to mindustry logic (mlog) compiler. https://xkcd.com/927/


## Website
Don't want to deal with all the annoying cli stuff? Try py2mlog out in your browser, at https://frantictoaster1024.github.io/py2mlog/.


## Install
```sh
# create and activate a venv
# i guess you could skip this if you wanted to
python -m venv .venv
.venv/Scripts/activate.bat  # or however you activate a venv in your shell
```

- With clipboard dependency (for copying output using CLI flags):
    ```sh
    pip install "py2mlog[clipboard] @ git+https://github.com/FranticToaster1024/py2mlog.git"
    ```


- Without clipboard dependency:
    ```sh
    pip install "py2mlog @ git+https://github.com/FranticToaster1024/py2mlog.git"
    ```

You could probably also use `pipx` or `uv`, but I'm not familiar with their CLIs.


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

You can compile multiple files/folders at once by passing them as space-separated arguments, like so:
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

You can use `-s` or `--stdout` to print the compiled mlog to stdout. This does not override or clash with the other outputs.

You can use `-c` or `--copy` to copy the compiled mlog to clipboard. This does not override or clash with the other outputs. This option requires the optional dependency 'pyperclip'.

You can use `--no-file` to disable the file output. This must be used with `-s`, `--stdout`, `-c`, or `--copy` otherwise the compiled program has nowhere to go.

Information, warnings, and other diagnostics are printed to stderr.


## Supported features
See [FEATURES.md](doc/FEATURES.md).


## Things to note
- **Do not** use any identifier prefixed with `__p2m`; they are reserved for the compiler.
- Error messages can sometimes be inaccurate or misleading.
- The compiler does not currently check and enforce the 1000 instruction mlog limit.


## WIP/To-do list
- radar instruction as method & builtin
- lookup
- avoid per-alias definitions in generated stub, mainly for functions with docstrings
- more optimization
- world instructions
- **Better errors**
- Inline mlog
- Config file?
- CLI upgrade?
- Passing functions (representing functions as line numbers instead of labels)
- Recursive functions (stack frames)


## AI assistance
Some testcases in `tests/` were generated using AI tools and reviewed/rewritten by me.
Additionally, AI assistance was used for configuration files (such as .github/workflows/ci.yml, pyproject.toml).
AI assistance was also used in some parts of the source code, such as [`func_utils.py`](src/py2mlog/compiler/func_utils.py) and [`script.js`](web/script.js). All source code was handwritten though.


## Credits
[mimex-data](https://github.com/cardillan/mimex-data) is the main source of data for stuff like mlog builtins, included in this repo as a submodule. I probably messed up here considering it has no license, so hey uh Cardillan if you want me to get rid of this I'm so sorry and feel free to let me know.

[pyodide](https://github.com/pyodide/pyodide) is used to run the py2mlog python package in a browser.

[pyndustric](https://codeberg.org/Lonami/pyndustric) was the main inspiration for this project. It's really cool, you should check it out! Also much of the user-facing api is identical to pyndustric fOr CoMpAtIbIlItY rEaSoNs!

[minpiler](https://github.com/neumond/minpiler) is really cool too!

Also, thank you to all contributors, users, and members of the mindustry community for your guidance and support!


## Contributing
All contributions are more than welcome!
More information can be found in [CONTRIBUTING.md](CONTRIBUTING.md).
