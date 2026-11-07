for (const textarea of document.querySelectorAll("textarea")) {
    textarea.addEventListener("keydown", e => {
        if (e.key !== "Tab") return;
        e.preventDefault();
        textarea.setRangeText("    ", textarea.selectionStart, textarea.selectionEnd, "end");
    });
}


const pyodide = await loadPyodide();

await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");
await micropip.install("./py2mlog-0.0.0-py3-none-any.whl.whl");

const ast_module = pyodide.pyimport("ast");
const compiler_module = pyodide.pyimport("py2mlog.compiler.compiler");
const emitter_module = pyodide.pyimport("py2mlog.compiler.emitter");
const codegen_module = pyodide.pyimport("py2mlog.mlog.codegen");


document.getElementById("editor").style.display = "flex";
document.getElementById("loading").style.display = "none";

const compile_button = document.getElementById("compile");
compile_button.addEventListener("click", () => {
    const src = document.getElementById("input").value;

    const emitter = emitter_module.Emitter();
    const compiler = compiler_module.Compiler(src, ast_module.parse(src), emitter);

    let out;
    try {
        compiler.compile();
        out = codegen_module.generate_mlog(emitter.instructions);
    } catch (error) {
        if (error instanceof pyodide.ffi.PythonError) {
            out = error.message;
        } else throw error;
    }

    document.getElementById("output").value = out;
});
