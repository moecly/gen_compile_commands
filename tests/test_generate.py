import json
import tempfile
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_compile_commands import generate_compile_commands_iter, save_compile_commands_iter, CompileCommand


def test_generate_compile_commands_iter(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "main.c").write_text("// main")
    (src_dir / "utils.c").write_text("// utils")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": ["include", "lib"],
        "defines": ["-DDEBUG", "-DNAME=Value"],
        "compiler": "gcc",
        "source_files": ["*.c"]
    }

    commands = list(generate_compile_commands_iter(config))

    assert len(commands) == 2
    assert all(isinstance(cmd, CompileCommand) for cmd in commands)

    cmd = commands[0]
    assert cmd.directory == str(src_dir)
    assert "gcc" in cmd.command
    assert "-Iinclude" in cmd.command
    assert "-Ilib" in cmd.command
    assert "-DDEBUG" in cmd.command
    assert "-DNAME=Value" in cmd.command
    assert ".c" in cmd.file


def test_generate_compile_commands_iter_no_files(tmp_path):
    config = {
        "source_dir": str(tmp_path),
        "include_dirs": [],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["*.c"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 0


def test_generate_compile_commands_iter_multiple_patterns(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "main.c").write_text("// main")
    (src_dir / "lib.cpp").write_text("// lib")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": [],
        "defines": [],
        "compiler": "g++",
        "source_files": ["*.c", "*.cpp"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 2


def test_generate_compile_commands_iter_recursive(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    sub_dir = src_dir / "sub"
    sub_dir.mkdir()

    (src_dir / "main.c").write_text("// main")
    (sub_dir / "nested.c").write_text("// nested")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": [],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 2


def test_generate_compile_commands_iter_exclude_dirs(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    build_dir = src_dir / "build"
    build_dir.mkdir()
    (build_dir / "generated.c").write_text("// generated")

    (src_dir / "main.c").write_text("// main")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": [],
        "exclude_dirs": ["build"],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 1
    assert "main.c" in commands[0].file
    assert "generated.c" not in commands[0].file


def test_generate_compile_commands_iter_exclude_multiple_dirs(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    build_dir = src_dir / "build"
    build_dir.mkdir()
    (build_dir / "build.c").write_text("// build")

    test_dir = src_dir / "test"
    test_dir.mkdir()
    (test_dir / "test.c").write_text("// test")

    (src_dir / "main.c").write_text("// main")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": [],
        "exclude_dirs": ["build", "test"],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 1
    assert "main.c" in commands[0].file


def test_generate_compile_commands_iter_exclude_nested_dir(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    nested_exclude = src_dir / "node_modules" / "package"
    nested_exclude.mkdir(parents=True)
    (nested_exclude / "dep.c").write_text("// dep")

    (src_dir / "main.c").write_text("// main")

    config = {
        "source_dir": str(src_dir),
        "include_dirs": [],
        "exclude_dirs": ["node_modules"],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }

    commands = list(generate_compile_commands_iter(config))
    assert len(commands) == 1
    assert "main.c" in commands[0].file


def test_save_compile_commands_iter(tmp_path):
    output_path = tmp_path / "compile_commands.json"

    commands = [
        CompileCommand(
            directory="/path/to/src",
            command="gcc -I. -c file1.c -o file1.o",
            file="/path/to/src/file1.c"
        ),
        CompileCommand(
            directory="/path/to/src",
            command="gcc -I. -c file2.c -o file2.o",
            file="/path/to/src/file2.c"
        )
    ]

    def cmd_iter():
        for cmd in commands:
            yield cmd

    save_compile_commands_iter(cmd_iter(), str(output_path))

    assert output_path.exists()

    with open(output_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["directory"] == "/path/to/src"
    assert data[0]["command"] == "gcc -I. -c file1.c -o file1.o"
    assert data[1]["file"] == "/path/to/src/file2.c"


def test_save_compile_commands_iter_empty(tmp_path):
    output_path = tmp_path / "compile_commands.json"

    def empty_iter():
        return
        yield

    save_compile_commands_iter(empty_iter(), str(output_path))

    assert output_path.exists()

    with open(output_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 0
