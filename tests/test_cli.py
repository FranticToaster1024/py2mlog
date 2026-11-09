from pathlib import Path

import pytest

from py2mlog.__main__ import main


def test_compile(tmp_path: Path):
    src = "x = 10"
    mlog = "set x 10"

    src_path = tmp_path / "src.py"
    out_path = tmp_path / "out.mlog"

    src_path.write_text(src, encoding="utf-8")

    main([str(src_path), "--output", str(out_path)])

    assert out_path.read_text(encoding="utf-8") == mlog


_test_output_file_exists_testcases = [
    pytest.param(
        "py2mlog {} --output {}",
        ["src.py", "out.mlog"],
        ["src.py"],
        ["out.mlog"],
        id="single-file-explicit-output",
    ),
    pytest.param(
        "py2mlog {}",
        ["file.py"],
        ["file.py"],
        ["file.mlog"],
        id="single-file-implicit-output",
    ),
    pytest.param(
        "py2mlog {} {} --output {} {}",
        ["src1.py", "src2.py", "out1.mlog", "out2.mlog"],
        ["src1.py", "src2.py"],
        ["out1.mlog", "out2.mlog"],
        id="multiple-files-explicit-output",
    ),
    pytest.param(
        "py2mlog {} {}",
        ["file1.py", "file2.py"],
        ["file1.py", "file2.py"],
        ["file1.mlog", "file2.mlog"],
        id="multiple-files-implicit-output",
    ),
    pytest.param(
        "py2mlog {} {} --output {} {}",
        [
            "dir1/dir2/src.py",
            "dir/src.py",
            "dir1/dir2/out.mlog",
            "out.mlog",
        ],
        ["dir1/dir2/src.py", "dir/src.py"],
        ["dir1/dir2/out.mlog", "out.mlog"],
        id="dir-files-explicit-output",
    ),
    pytest.param(
        "py2mlog {} {}",
        ["dir1/dir2/file.py", "dir/file.py"],
        ["dir1/dir2/file.py", "dir/file.py"],
        ["dir1/dir2/file.mlog", "dir/file.mlog"],
        id="dir-files-implicit-output",
    ),
    pytest.param(
        "py2mlog {} {} --output {} {}",
        ["dir/", "dir1/dir2/", "out_dir/", "./"],
        [
            "dir/file1.py",
            "dir/file2.py",
            "dir/config.json",
            "dir1/dir2/file.py",
        ],
        ["out_dir/file1.mlog", "out_dir/file2.mlog", "file.mlog"],
        id="dir-explicit-output",
    ),
    pytest.param(
        "py2mlog {} {}",
        ["dir/", "dir1/dir2/"],
        [
            "dir/file1.py",
            "dir/file2.py",
            "dir/config.json",
            "dir1/dir2/file.py",
        ],
        ["dir/file1.mlog", "dir/file2.mlog", "dir1/dir2/file.mlog"],
        id="dir-implicit-output",
    ),
    pytest.param(
        "py2mlog {} {} --output {} {}",
        ["src.py", "dir/", "out.mlog", "out_dir/out.mlog"],
        ["src.py", "dir/src.py"],
        ["out.mlog", "out_dir/out.mlog"],
        id="file-and-dir-explicit-output",
    ),
    pytest.param(
        "py2mlog {} {}",
        ["file.py", "dir/"],
        ["file.py", "dir/file.py"],
        ["file.mlog", "dir/file.mlog"],
        id="file-and-dir-implicit-output",
    ),
]


@pytest.mark.parametrize(
    ("cmd", "path_args", "input_files", "output_files"),
    _test_output_file_exists_testcases,
)
def test_output_file_exists(
    cmd: str,
    path_args: list[str],
    input_files: list[str],
    output_files: list[str],
    tmp_path: Path,
):
    for file in input_files:
        path = tmp_path / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("pass")

    full_path_args = [str(tmp_path / p) for p in path_args]
    formatted_cmd = cmd.format(*full_path_args)
    cmd_name, *argv = formatted_cmd.split()
    assert cmd_name == "py2mlog"
    main(argv)

    for file in output_files:
        path = tmp_path / file
        assert path.exists()
