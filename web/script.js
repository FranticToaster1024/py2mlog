const input_textarea = document.getElementById("input");
input_textarea.addEventListener("keydown", e => {
    if (e.key === "Tab") {
        e.preventDefault();
        textarea.setRangeText("    ", textarea.selectionStart, textarea.selectionEnd, "end");
    } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        compile();
    }
});


const live_btn = document.getElementById("live");
live_btn.addEventListener("click", () => {
    const pressed = live_btn.ariaPressed == "true" ? "false" : "true";
    live_btn.ariaPressed = pressed;

    if (pressed == "true") {
        compile();
    }
});


const MIN_DT_MS = 100;
let last_input = 0;

input_textarea.addEventListener("input", () => {
    if (live_btn.ariaPressed !== "true") return;
    const now = performance.now();
    if (now - last_input >= MIN_DT_MS) {
        last_input = now;
        compile();
    }
});


const outputElement = document.getElementById("output");

const copy_btn = document.getElementById("copy");
copy_btn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(outputElement.value);
});


const pyodide = await loadPyodide();

await pyodide.loadPackage("micropip");
const micropip = pyodide.pyimport("micropip");
await micropip.install("./py2mlog-0.0.0-py3-none-any.whl");

const ast_module = pyodide.pyimport("ast");
const compiler_module = pyodide.pyimport("py2mlog.compiler.compiler");
const emitter_module = pyodide.pyimport("py2mlog.compiler.emitter");
const codegen_module = pyodide.pyimport("py2mlog.mlog.codegen");


document.getElementById("editor").style.display = "flex";
document.getElementById("loading").style.display = "none";

const compile_button = document.getElementById("compile");
compile_button.addEventListener("click", compile);


function compile() {
    const src = document.getElementById("input").value;

    const emitter = emitter_module.Emitter();

    let text_color = "";
    let output;

    let copy_btn_bg_col = "";
    let copy_btn_border_col = "";
    let copy_btn_text = "Copy";
    try {
        const compiler = compiler_module.Compiler(src, ast_module.parse(src), emitter);
        compiler.compile();
        output = codegen_module.generate_mlog(emitter.instructions);
    } catch (error) {
        if (error instanceof pyodide.ffi.PythonError) {
            output = error.message;
            text_color = "#e57373";

            copy_btn_bg_col = "#eb5d5d";
            copy_btn_border_col = "#dc5050";
            copy_btn_text = "Copy Error"
        } else throw error;
    }

    outputElement.value = output;
    outputElement.style.color = text_color;

    copy_btn.style.backgroundColor = copy_btn_bg_col;
    copy_btn.style.borderColor = copy_btn_border_col;
    copy_btn.textContent = copy_btn_text;
}