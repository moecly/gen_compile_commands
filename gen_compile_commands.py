import os
import json
import glob
import sys


def load_config(config_path, verbose=False):
    """Load the configuration from the given JSON file."""
    if verbose:
        print(f"Loading configuration from {config_path}")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {config_path} as JSON.")
        sys.exit(1)

    if verbose:
        print(f"Configuration loaded:")
        print(f"source_dir: {config['source_dir']}")
        print(f"include_dirs: {config['include_dirs']}")
        print(f"defines: {config['defines']}")
        print(f"compiler: {config['compiler']}")
        print(f"source_files: {config['source_files']}")

    return config


def generate_compile_commands_iter(config, verbose=False):
    """Generate the compile commands from the configuration as an iterator."""
    source_dir = config["source_dir"]
    include_dirs = config["include_dirs"]
    defines = config["defines"]
    compiler = config["compiler"]
    source_files = config["source_files"]

    if verbose:
        print(f"Macros defined: {defines}")

    # Iterate through patterns
    for pattern in source_files:
        # Use iglob for memory efficiency - it returns an iterator, not a list
        files_iterator = glob.iglob(os.path.join(source_dir, pattern), recursive=True)

        if verbose:
            print(f"Processing pattern: {pattern}")

        # Generate compile command for each file as it's found
        for source_file in files_iterator:
            command = {
                "directory": source_dir,
                "command": f"{compiler} {' '.join(['-I' + d for d in include_dirs])} "
                f"{' '.join(defines)} -c {source_file} -o {source_file}.o",
                "file": source_file,
            }
            # 'yield' turns this function into a generator
            yield command


def save_compile_commands_iter(commands_iterator, output_path, verbose=False):
    """Save the generated compile commands from an iterator to a JSON file."""
    if verbose:
        print(f"Saving compile commands to {output_path}")
    try:
        with open(output_path, "w") as f:
            f.write("[\n")  # Start of JSON array
            first = True
            for command in commands_iterator:
                if not first:
                    f.write(",\n")  # Add comma before the next item
                json.dump(command, f, indent=4)
                first = False
            f.write("\n]\n")  # End of JSON array
    except IOError:
        print(f"Error: Failed to save compile commands to {output_path}.")
        sys.exit(1)

    if verbose:
        print("compile_commands.json has been generated")


def generate_config_template(output_path, add_subdirs=False, verbose=False):
    """Generate a .gen_compile_commands_cfg.json template file with options."""
    # Get the current working directory (absolute path) for source_dir
    source_dir = os.path.abspath(os.getcwd())

    # If add_subdirs is True, find all subdirectories for include_dirs
    include_dirs = []
    if add_subdirs:
        if verbose:
            print("Generating include_dirs by adding all subdirectories:")
        for root, dirs, files in os.walk(source_dir):
            for dir_name in dirs:
                include_dirs.append(os.path.join(root, dir_name))
                if verbose:
                    print(f"Added to include_dirs: {os.path.join(root, dir_name)}")

    # Template with absolute source_dir and include_dirs if needed
    template = {
        "source_dir": source_dir,
        "include_dirs": include_dirs
        if add_subdirs
        else ["path/to/include1", "path/to/include2"],
        "defines": ["-DDEBUG", "-DANOTHER_MACRO"],
        "compiler": "gcc",
        "source_files": ["**/*.c", "**/*.cpp"],
    }

    try:
        with open(output_path, "w") as f:
            json.dump(template, f, indent=4)
    except IOError:
        print(f"Error: Failed to save template to {output_path}.")
        sys.exit(1)

    if verbose:
        print(f"Template config file generated at {output_path}")
    else:
        print(f"Template config file generated at {output_path}")


def print_help():
    """Print usage instructions."""
    print("""
Usage: gen_compile_commands [options]

Options:
  -v                  Enable verbose mode (prints detailed information)
  -f <file_or_dir>    Specify the configuration file or directory containing the config
  -g                  Generate the config template file (.gen_compile_commands_cfg.json)
  -i                  Include subdirectories in the config template
  -h                  Show this help message
""")


def main():
    """Main function to handle user input and generate compile_commands.json."""
    verbose = False
    config_path = None  # Default config path is None (to be set later)
    add_subdirs = False  # Default for -i flag (to be set later)

    # ... (Argument parsing logic is fine, no changes needed here) ...
    if len(sys.argv) == 1:
        config_path = ".gen_compile_commands_cfg.json"
    else:
        if "-h" in sys.argv:
            print_help()
            sys.exit(0)
        if "-v" in sys.argv:
            verbose = True
            sys.argv.remove("-v")
        if "-f" in sys.argv:
            if len(sys.argv) < 3:
                print("Error: -f requires a path to a directory or JSON config file.")
                sys.exit(1)
            input_path = sys.argv[2]
            if os.path.isdir(input_path):
                config_path = os.path.join(input_path, ".gen_compile_commands_cfg.json")
                if not os.path.exists(config_path):
                    print(f"Error: {config_path} does not exist.")
                    sys.exit(1)
            elif os.path.isfile(input_path) and input_path.endswith(".json"):
                config_path = input_path
            else:
                print(
                    "Error: Invalid path. Please provide a valid directory or JSON config file."
                )
                sys.exit(1)
        else:
            config_path = ".gen_compile_commands_cfg.json"
        if "-g" in sys.argv:
            if "-i" in sys.argv:
                add_subdirs = True
                sys.argv.remove("-i")
            generate_config_template(
                ".gen_compile_commands_cfg.json", add_subdirs, verbose
            )
            return

    if not config_path:
        # Check if config path was determined after parsing args
        if os.path.exists(".gen_compile_commands_cfg.json"):
            config_path = ".gen_compile_commands_cfg.json"
        else:
            print("Error: Configuration file .gen_compile_commands_cfg.json not found.")
            sys.exit(1)

    # Load the configuration and generate compile_commands.json
    config = load_config(config_path, verbose)
    # Get the iterator from the generator function
    commands_iterator = generate_compile_commands_iter(config, verbose)
    # Pass the iterator to the streaming save function
    save_compile_commands_iter(commands_iterator, "compile_commands.json", verbose)

    if not verbose:
        print("compile_commands.json has been successfully generated.")


if __name__ == "__main__":
    main()
