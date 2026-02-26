# Gen Compile Commands

`gen_compile_commands` is a tool used to generate a `compile_commands.json` file for C/C++ projects. It extracts relevant information from a given configuration file and generates a list of commands used for compiling the project, which can be integrated into IDEs or other build tools.

## Features

- **Generate Compile Commands**: Generate a `compile_commands.json` file based on project configuration, suitable for tools like `clangd`.
- **Generate Config Template**: Generate a config template file `.gen_compile_commands_cfg.json` using the `-g` option, which can be quickly modified to create project configuration files.
- **Support Recursive Include Directories**: Automatically include all subdirectories in the `include_dirs` field via the `-i` option.
- **Verbose Mode**: Enable detailed output using the `-v` option to view the execution process of the tool.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/moecly/gen_compile_commands.git
   ```

1. Navigate to the project directory:

   ```bash
   cd gen_compile_commands
   ```

## Usage

### 1. Print Help Information

Use the `-h` option to view the usage instructions:

```bash
python gen_compile_commands.py -h
```

Output:

```
Usage: gen_compile_commands [options]

Options:
  -v                  Enable verbose mode (prints detailed information)
  -f <file_or_dir>    Specify the configuration file or directory containing the config
  -g                  Generate the config template file (.gen_compile_commands_cfg.json)
  -i                  Include subdirectories in the config template
  -h                  Show this help message
```

### 2. Generate `compile_commands.json`

You can generate the `compile_commands.json` file by specifying the configuration file path:

```bash
python gen_compile_commands.py -f /path/to/config.json
```

If the configuration file is located in the current directory, the command can be simplified:

```bash
python gen_compile_commands.py -v
```

### 3. Generate Config Template

If you don't have an existing configuration file, you can generate a template file using the `-g` option:

```bash
python gen_compile_commands.py -g
```

If you need to include all subdirectories in the template, use the `-i` option:

```bash
python gen_compile_commands.py -g -i
```

The generated template file is `.gen_compile_commands_cfg.json`, which can be modified as per your project needs.

### 4. Enable Verbose Mode

Use the `-v` option to enable verbose mode and view the execution process in detail:

```bash
python gen_compile_commands.py -v
```

### 5. Generate Template Including Subdirectories

Use the `-i` option when generating the template to automatically include all subdirectories:

```bash
python gen_compile_commands.py -g -i
```

## Compile into ELF Executable

If you want to package `gen_compile_commands` into a standalone ELF executable, you can use [PyInstaller](https://pyinstaller.org/):

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Use the `--onefile` option to package the script:

   ```bash
   pyinstaller --onefile gen_compile_commands.py
   ```

3. After packaging, you can find the generated ELF file in the `dist` directory. Run the ELF file directly:

   ```bash
   ./dist/gen_compile_commands
   ```

## Configuration File Explanation

`gen_compile_commands` generates compile commands by reading a JSON configuration file. The configuration file contains the following fields:

- **source_dir**: The root directory of the source code (absolute path).
- **include_dirs**: The directories to be included during compilation (list, can include multiple paths).
- **defines**: The macros to be defined during compilation (list).
- **compiler**: The path or command of the compiler (e.g., `gcc`).
- **source_files**: The file patterns for source code files (supports wildcards like `"**/*.c"`).

### Sample Configuration File

```json
{
  "source_dir": "/path/to/source",
  "include_dirs": [
    "/path/to/include1",
    "/path/to/include2"
  ],
  "defines": [
    "-DDEBUG",
    "-DANOTHER_MACRO"
  ],
  "compiler": "gcc",
  "source_files": [
    "**/*.c",
    "**/*.cpp"
  ]
}
```

## Frequently Asked Questions

### 1. How can I specify include directories (`include_dirs`)?

You can manually specify the directories to include in the configuration file or use the `-i` option to automatically include all subdirectories.

### 2. How can I view the generated commands?

Enable verbose mode with the `-v` option to see detailed information about the process and the generated commands.

### 3. How can I generate a custom configuration file?

Use the `-g` option to generate the template file and modify it according to your needs.

## Contributing

If you have suggestions or issues, feel free to submit an Issue or Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
