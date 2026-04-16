import json
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_compile_commands import validate_config, load_config, generate_config_template


def test_validate_config_valid():
    config = {
        "source_dir": "/path/to/source",
        "include_dirs": ["path/to/include"],
        "defines": ["-DDEBUG"],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }
    errors = validate_config(config)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_validate_config_valid_with_exclude_dirs():
    config = {
        "source_dir": "/path/to/source",
        "include_dirs": ["path/to/include"],
        "exclude_dirs": [".git", "node_modules"],
        "defines": ["-DDEBUG"],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }
    errors = validate_config(config)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_validate_config_missing_source_dir():
    config = {
        "include_dirs": ["path/to/include"],
        "defines": ["-DDEBUG"],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }
    errors = validate_config(config)
    assert "Missing required field: 'source_dir'" in errors


def test_validate_config_missing_all_fields():
    config = {}
    errors = validate_config(config)
    assert len(errors) == 5


def test_validate_config_invalid_types():
    config = {
        "source_dir": 123,
        "include_dirs": "not an array",
        "defines": 456,
        "compiler": [],
        "source_files": "not an array"
    }
    errors = validate_config(config)
    assert "'source_dir' must be a string" in errors
    assert "'include_dirs' must be an array" in errors
    assert "'defines' must be an array" in errors
    assert "'compiler' must be a string" in errors
    assert "'source_files' must be an array" in errors


def test_validate_config_invalid_array_items():
    config = {
        "source_dir": "/path",
        "include_dirs": [123, "string"],
        "defines": ["-D", 456],
        "compiler": "gcc",
        "source_files": [True, "*.c"]
    }
    errors = validate_config(config)
    assert "All items in 'include_dirs' must be strings" in errors
    assert "All items in 'defines' must be strings" in errors
    assert "All items in 'source_files' must be strings" in errors


def test_validate_config_invalid_exclude_dirs():
    config = {
        "source_dir": "/path",
        "include_dirs": [],
        "exclude_dirs": [123, "string"],
        "defines": [],
        "compiler": "gcc",
        "source_files": ["*.c"]
    }
    errors = validate_config(config)
    assert "All items in 'exclude_dirs' must be strings" in errors


def test_load_config_file_not_found():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        os.unlink(temp_path)
        result = load_config(temp_path)
        assert False, "Should have exited"
    except SystemExit:
        pass


def test_load_config_invalid_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name

    try:
        os.unlink(temp_path)
        load_config(temp_path)
        assert False, "Should have exited"
    except SystemExit:
        pass
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_load_config_valid_file():
    config = {
        "source_dir": "/path/to/source",
        "include_dirs": ["path/to/include"],
        "defines": ["-DDEBUG"],
        "compiler": "gcc",
        "source_files": ["**/*.c"]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        result = load_config(temp_path)
        assert result == config
    finally:
        os.unlink(temp_path)


def test_generate_config_template():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        generate_config_template(temp_path, add_subdirs=False)
        assert os.path.exists(temp_path)

        with open(temp_path, 'r') as f:
            template = json.load(f)

        assert "source_dir" in template
        assert "include_dirs" in template
        assert "exclude_dirs" in template
        assert "defines" in template
        assert "compiler" in template
        assert "source_files" in template
        assert template["include_dirs"] == ["path/to/include1", "path/to/include2"]
        assert ".*" in template["exclude_dirs"]
        assert "build*" in template["exclude_dirs"]
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_generate_config_template_with_subdirs(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        os.makedirs("subdir1")
        os.makedirs("subdir2/nested")
        template_path = ".gen_compile_commands_cfg.json"
        generate_config_template(template_path, add_subdirs=True)

        with open(template_path, 'r') as f:
            template = json.load(f)

        assert len(template["include_dirs"]) > 0
        assert any("subdir1" in d for d in template["include_dirs"])
        assert ".*" in template["exclude_dirs"]
    finally:
        os.chdir(old_cwd)
        if os.path.exists(template_path):
            os.unlink(template_path)


def test_generate_config_template_with_extra_exclude_dirs(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        template_path = ".gen_compile_commands_cfg.json"
        generate_config_template(template_path, add_subdirs=False, extra_exclude_dirs=["test", "examples"])

        with open(template_path, 'r') as f:
            template = json.load(f)

        assert "test" in template["exclude_dirs"]
        assert "examples" in template["exclude_dirs"]
    finally:
        os.chdir(old_cwd)
        if os.path.exists(template_path):
            os.unlink(template_path)
