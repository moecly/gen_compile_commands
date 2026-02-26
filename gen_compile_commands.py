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


def generate_compile_commands(config, verbose=False):
    """Generate the compile commands from the configuration."""
    source_dir = config["source_dir"]
    include_dirs = config["include_dirs"]
    defines = config["defines"]
    compiler = config["compiler"]
    source_files = config["source_files"]

    commands = []

    # Print macros if verbose
    if verbose:
        print(f"Macros defined: {defines}")

    # Iterate through source files and match files
    all_files = []
    for pattern in source_files:
        files = glob.glob(os.path.join(source_dir, pattern), recursive=True)

        if verbose:
            print(f"Pattern: {pattern} -> Found files: {files}")

        all_files.extend(files)

    # If verbose, print the list of all source files
    if verbose:
        print(f"All source files found: {all_files}")

    # Generate compile command for each file
    for source_file in all_files:
        command = {
            "directory": source_dir,
            "command": f"{compiler} {' '.join(['-I' + d for d in include_dirs])} "
            f"{' '.join(defines)} -c {source_file} -o {source_file}.o",
            "file": source_file,
        }
        commands.append(command)

    return commands, all_files


def save_compile_commands(commands, output_path, verbose=False):
    """Save the generated compile commands to a JSON file."""
    if verbose:
        print(f"Saving compile commands to {output_path}")
    try:
        with open(output_path, "w") as f:
            json.dump(commands, f, indent=4)
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

    # Check for command line arguments
    if len(sys.argv) == 1:
        # If no arguments are provided, set config_path to the default config file in the current directory
        config_path = ".gen_compile_commands_cfg.json"
    else:
        # Handle options like -v, -f, -g, -h, and -i
        if "-h" in sys.argv:
            print_help()
            sys.exit(0)

        if "-v" in sys.argv:
            verbose = True
            sys.argv.remove("-v")  # Remove the -v option so it doesn't interfere

        if "-f" in sys.argv:
            # If the -f option is provided, expect a directory path or a JSON file
            if len(sys.argv) < 3:
                print("Error: -f requires a path to a directory or JSON config file.")
                sys.exit(1)

            input_path = sys.argv[
                2
            ]  # The next argument after -f is the path to the config
            if os.path.isdir(input_path):
                # If it's a directory, check for .gen_compile_commands_cfg.json inside it
                config_path = os.path.join(input_path, ".gen_compile_commands_cfg.json")
                if not os.path.exists(config_path):
                    print(f"Error: {config_path} does not exist.")
                    sys.exit(1)
            elif os.path.isfile(input_path) and input_path.endswith(".json"):
                # If it's a JSON file, use it directly
                config_path = input_path
            else:
                print(
                    "Error: Invalid path. Please provide a valid directory or JSON config file."
                )
                sys.exit(1)
        else:
            config_path = ".gen_compile_commands_cfg.json"

        if "-g" in sys.argv:
            # Generate the config template
            if "-i" in sys.argv:
                # If `-i` flag is provided, enable the "brutal" include_dirs generation
                add_subdirs = True
                sys.argv.remove("-i")  # Remove the -i option so it doesn't interfere

            # Generate the template
            generate_config_template(
                ".gen_compile_commands_cfg.json", add_subdirs, verbose
            )
            return

    # If no config_path is set, we use the default config in the current directory
    if not config_path:
        print(
            "Error: Configuration file path is not provided. Use -f to specify a config file."
        )
        sys.exit(1)

    # Load the configuration and generate compile_commands.json
    config = load_config(config_path, verbose)
    commands, all_files = generate_compile_commands(config, verbose)
    save_compile_commands(commands, "compile_commands.json", verbose)

    # Print success message if not in verbose mode
    if verbose:
        print(f"All source files: {all_files}")
    else:
        print("compile_commands.json has been successfully generated.")


if __name__ == "__main__":
    main()
