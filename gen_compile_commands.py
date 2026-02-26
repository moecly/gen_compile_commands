import os
import json
import glob
import sys


def load_config(config_path):
    """Load the configuration from the given JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def generate_compile_commands(config):
    """Generate the compile commands from the configuration."""
    source_dir = config["source_dir"]
    include_dirs = config["include_dirs"]
    defines = config["defines"]
    compiler = config["compiler"]
    source_files = config["source_files"]

    commands = []

    # Iterate through source files and match files
    for pattern in source_files:
        files = glob.glob(os.path.join(source_dir, pattern), recursive=True)

        for file in files:
            command = {
                "directory": source_dir,
                "command": f"{compiler} {' '.join(['-I' + d for d in include_dirs])} "
                f"{' '.join(defines)} -c {file} -o {file}.o",
                "file": file,
            }
            commands.append(command)

    return commands


def save_compile_commands(commands, output_path):
    """Save the generated compile commands to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(commands, f, indent=4)


def generate_config_template(output_path):
    """Generate a .gen_compile_commands_cfg.json template file."""
    template = {
        "source_dir": "path/to/source",
        "include_dirs": ["path/to/include1", "path/to/include2"],
        "defines": ["-DDEBUG", "-DANOTHER_MACRO"],
        "compiler": "gcc",
        "source_files": ["**/*.c", "**/*.cpp"],
    }

    with open(output_path, "w") as f:
        json.dump(template, f, indent=4)

    print(f"Template config file generated at {output_path}")


def main():
    """Main function to handle user input and generate compile_commands.json."""
    if len(sys.argv) == 1:
        # No arguments passed, try to read .gen_compile_commands_cfg.json from the current directory
        config_path = ".gen_compile_commands_cfg.json"
        if not os.path.exists(config_path):
            print(f"Error: {config_path} does not exist.")
            sys.exit(1)
    elif sys.argv[1] == "-g":
        # Generate the config template
        generate_config_template(".gen_compile_commands_cfg.json")
        return
    else:
        # Get the config file path or directory from command line argument
        input_path = sys.argv[1]

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
                "Error: Invalid input. Please provide a valid directory or JSON config file."
            )
            sys.exit(1)

    # Load the configuration and generate compile_commands.json
    config = load_config(config_path)
    commands = generate_compile_commands(config)
    save_compile_commands(commands, "compile_commands.json")

    print("compile_commands.json has been generated")


if __name__ == "__main__":
    main()
