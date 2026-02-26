import os
import json
import glob
import sys


def load_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def generate_compile_commands(config):
    # Get configuration
    source_dir = config["source_dir"]
    include_dirs = config["include_dirs"]
    defines = config["defines"]
    compiler = config["compiler"]
    source_files = config["source_files"]

    # Store compile commands
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
    with open(output_path, "w") as f:
        json.dump(commands, f, indent=4)


def main():
    # Get the config file path from command line argument or default to current directory
    if len(sys.argv) > 1:
        config_path = sys.argv[1]  # Get config path from first argument
    else:
        config_path = ".gen_compile_commands_cfg.json"  # Default to current directory

    # Generate compile_commands.json
    config = load_config(config_path)
    commands = generate_compile_commands(config)
    save_compile_commands(commands, "compile_commands.json")

    print("compile_commands.json has been generated")


if __name__ == "__main__":
    main()
