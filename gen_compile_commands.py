import os
import sys
import json
import glob
import logging
from typing import Iterator, Dict, Any, List, Optional
from dataclasses import dataclass


CONFIG_SCHEMA = {
    "type": "object",
    "required": ["source_dir", "include_dirs", "defines", "compiler", "source_files"],
    "properties": {
        "source_dir": {"type": "string"},
        "include_dirs": {"type": "array", "items": {"type": "string"}},
        "defines": {"type": "array", "items": {"type": "string"}},
        "compiler": {"type": "string"},
        "source_files": {"type": "array", "items": {"type": "string"}}
    }
}


@dataclass
class CompileCommand:
    directory: str
    command: str
    file: str


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout
    )


def validate_config(config: Dict[str, Any]) -> List[str]:
    errors = []

    for field in CONFIG_SCHEMA["required"]:
        if field not in config:
            errors.append(f"Missing required field: '{field}'")

    if "source_dir" in config and not isinstance(config["source_dir"], str):
        errors.append("'source_dir' must be a string")

    if "include_dirs" in config:
        if not isinstance(config["include_dirs"], list):
            errors.append("'include_dirs' must be an array")
        elif not all(isinstance(d, str) for d in config["include_dirs"]):
            errors.append("All items in 'include_dirs' must be strings")

    if "defines" in config:
        if not isinstance(config["defines"], list):
            errors.append("'defines' must be an array")
        elif not all(isinstance(d, str) for d in config["defines"]):
            errors.append("All items in 'defines' must be strings")

    if "compiler" in config and not isinstance(config["compiler"], str):
        errors.append("'compiler' must be a string")

    if "source_files" in config:
        if not isinstance(config["source_files"], list):
            errors.append("'source_files' must be an array")
        elif not all(isinstance(f, str) for f in config["source_files"]):
            errors.append("All items in 'source_files' must be strings")

    return errors


def load_config(config_path: str, verbose: bool = False) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)
    logger.debug(f"Loading configuration from {config_path}")

    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {config_path} as JSON: {e}")
        sys.exit(1)

    errors = validate_config(config)
    if errors:
        for error in errors:
            logger.error(error)
        sys.exit(1)

    if verbose:
        logger.info("Configuration loaded:")
        logger.info(f"  source_dir: {config['source_dir']}")
        logger.info(f"  include_dirs: {config['include_dirs']}")
        logger.info(f"  defines: {config['defines']}")
        logger.info(f"  compiler: {config['compiler']}")
        logger.info(f"  source_files: {config['source_files']}")

    return config


def generate_compile_commands_iter(
    config: Dict[str, Any], verbose: bool = False
) -> Iterator[CompileCommand]:
    logger = logging.getLogger(__name__)

    source_dir: str = config["source_dir"]
    include_dirs: List[str] = config["include_dirs"]
    defines: List[str] = config["defines"]
    compiler: str = config["compiler"]
    source_files: List[str] = config["source_files"]

    if verbose:
        logger.debug(f"Macros defined: {defines}")

    for pattern in source_files:
        if verbose:
            logger.debug(f"Processing pattern: {pattern}")

        files_iterator = glob.iglob(os.path.join(source_dir, pattern), recursive=True)

        for source_file in files_iterator:
            command_str = " ".join([f"-I{d}" for d in include_dirs])
            command_str = f"{compiler} {command_str} {' '.join(defines)} -c {source_file} -o {source_file}.o"

            yield CompileCommand(
                directory=source_dir,
                command=command_str,
                file=source_file
            )


def save_compile_commands_iter(
    commands_iterator: Iterator[CompileCommand],
    output_path: str,
    verbose: bool = False
) -> None:
    logger = logging.getLogger(__name__)

    if verbose:
        logger.debug(f"Saving compile commands to {output_path}")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("[\n")
            first = True
            for cmd in commands_iterator:
                if not first:
                    f.write(",\n")
                json.dump({
                    "directory": cmd.directory,
                    "command": cmd.command,
                    "file": cmd.file
                }, f, indent=4)
                first = False
            f.write("\n]\n")
    except IOError as e:
        logger.error(f"Failed to save compile commands to {output_path}: {e}")
        sys.exit(1)

    if verbose:
        logger.info("compile_commands.json has been generated")


def generate_config_template(
    output_path: str,
    add_subdirs: bool = False,
    verbose: bool = False
) -> None:
    logger = logging.getLogger(__name__)

    source_dir = os.path.abspath(os.getcwd())

    include_dirs: List[str] = []
    if add_subdirs:
        logger.debug("Generating include_dirs by adding all subdirectories:")
        for root, dirs, _ in os.walk(source_dir):
            for dir_name in dirs:
                full_path = os.path.join(root, dir_name)
                include_dirs.append(full_path)
                logger.debug(f"  Added: {full_path}")

    template: Dict[str, Any] = {
        "source_dir": source_dir,
        "include_dirs": include_dirs if add_subdirs else ["path/to/include1", "path/to/include2"],
        "defines": ["-DDEBUG", "-DANOTHER_MACRO"],
        "compiler": "gcc",
        "source_files": ["**/*.c", "**/*.cpp"]
    }

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=4)
    except IOError as e:
        logger.error(f"Failed to save template to {output_path}: {e}")
        sys.exit(1)

    logger.info(f"Template config file generated at {output_path}")


def print_help() -> None:
    print("""
Usage: gen_compile_commands [options]

Options:
  -v                  Enable verbose mode (prints detailed information)
  -f <file_or_dir>    Specify the configuration file or directory containing the config
  -g                  Generate the config template file (.gen_compile_commands_cfg.json)
  -i                  Include subdirectories in the config template
  -h                  Show this help message
""")


def main() -> None:
    verbose = False
    config_path: Optional[str] = None
    add_subdirs = False

    if len(sys.argv) == 1:
        config_path = ".gen_compile_commands_cfg.json"
    else:
        if "-h" in sys.argv:
            print_help()
            sys.exit(0)
        if "-v" in sys.argv:
            verbose = True
            sys.argv.remove("-v")

        setup_logging(verbose)

        if "-f" in sys.argv:
            idx = sys.argv.index("-f")
            if len(sys.argv) <= idx + 1:
                print("Error: -f requires a path to a directory or JSON config file.")
                sys.exit(1)
            input_path = sys.argv[idx + 1]
            if os.path.isdir(input_path):
                config_path = os.path.join(input_path, ".gen_compile_commands_cfg.json")
                if not os.path.exists(config_path):
                    print(f"Error: {config_path} does not exist.")
                    sys.exit(1)
            elif os.path.isfile(input_path) and input_path.endswith(".json"):
                config_path = input_path
            else:
                print("Error: Invalid path. Please provide a valid directory or JSON config file.")
                sys.exit(1)
        else:
            config_path = ".gen_compile_commands_cfg.json"

        if "-g" in sys.argv:
            if "-i" in sys.argv:
                add_subdirs = True
                sys.argv.remove("-i")
            setup_logging(verbose)
            generate_config_template(".gen_compile_commands_cfg.json", add_subdirs, verbose)
            return

    if not config_path:
        if os.path.exists(".gen_compile_commands_cfg.json"):
            config_path = ".gen_compile_commands_cfg.json"
        else:
            print("Error: Configuration file .gen_compile_commands_cfg.json not found.")
            sys.exit(1)

    setup_logging(verbose)
    config = load_config(config_path, verbose)
    commands_iterator = generate_compile_commands_iter(config, verbose)
    save_compile_commands_iter(commands_iterator, "compile_commands.json", verbose)

    if not verbose:
        print("compile_commands.json has been successfully generated.")


if __name__ == "__main__":
    main()
