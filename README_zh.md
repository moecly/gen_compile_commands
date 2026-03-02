<div align="center">

**[English](./README.md) | [简体中文](./README_zh.md)**

</div>

---

# Gen Compile Commands (生成 compile_commands.json 工具)

`gen_compile_commands` 是一个用于为 C/C++ 项目生成 `compile_commands.json` 文件的工具。它通过读取指定的配置文件，提取项目相关信息，并生成用于编译项目的命令列表，这些信息可以被集成到 IDE 或其他构建工具中（如 `clangd`）。

## ✨ 功能特性

- **生成编译命令**: 基于项目配置生成 `compile_commands.json` 文件，适用于 `clangd` 等工具。
- **生成配置模板**: 使用 `-g` 选项生成一个配置模板文件 `.gen_compile_commands_cfg.json`，方便快速创建项目配置文件。
- **支持递归包含目录**: 通过 `-i` 选项，可以自动将项目所有子目录添加到 `include_dirs` 字段中。
- **详细模式**: 使用 `-v` 选项启用详细输出，以查看工具的执行过程。

## 🚀 安装

1. 克隆本仓库：

   ```bash
   git clone https://github.com/moecly/gen_compile_commands.git
   ```

2. 进入项目目录：

   ```bash
   cd gen_compile_commands
   ```

## 📝 使用方法

### 1. 打印帮助信息

使用 `-h` 选项查看使用说明：

```bash
python gen_compile_commands.py -h
```

输出：

```
Usage: gen_compile_commands [options]

Options:
  -v                  Enable verbose mode (prints detailed information)
  -f <file_or_dir>    Specify the configuration file or directory containing the config
  -g                  Generate the config template file (.gen_compile_commands_cfg.json)
  -i                  Include subdirectories in the config template
  -h                  Show this help message
```

### 2. 生成 `compile_commands.json`

你可以通过指定配置文件的路径来生成 `compile_commands.json` 文件：

```bash
python gen_compile_commands.py -f /path/to/config.json
```

如果配置文件位于当前目录下（且名为 `.gen_compile_commands_cfg.json`），命令可以简化为：

```bash
python gen_compile_commands.py
```

### 3. 生成配置模板

如果你还没有配置文件，可以使用 `-g` 选项生成一个模板文件：

```bash
python gen_compile_commands.py -g
```

如果需要让模板自动包含所有子目录，请使用 `-i` 选项：

```bash
python gen_compile_commands.py -g -i
```

生成的模板文件名为 `.gen_compile_commands_cfg.json`，你可以根据你的项目需求对其进行修改。

### 4. 启用详细模式

使用 `-v` 选项启用详细模式，以查看详细的执行过程：

```bash
python gen_compile_commands.py -v
```

### 5. 生成包含子目录的模板

在生成模板时使用 `-i` 选项，可以自动将所有子目录添加到 `include_dirs` 中：

```bash
python gen_compile_commands.py -g -i
```

## 📦 编译为可执行文件

如果你想将 `gen_compile_commands` 打包成一个独立的 ELF 可执行文件，可以使用 [PyInstaller](https://pyinstaller.org/)：

1. 安装 PyInstaller：

   ```bash
   pip install pyinstaller
   ```

2. 使用 `--onefile` 选项打包脚本：

   ```bash
   pyinstaller --onefile gen_compile_commands.py
   ```

3. 打包完成后，你可以在 `dist` 目录下找到生成的可执行文件。直接运行它即可：

   ```bash
   ./dist/gen_compile_commands
   ```

## 📄 配置文件说明

`gen_compile_commands` 通过读取一个 JSON 格式的配置文件来工作。该文件包含以下字段：

- **source_dir**: 源代码的根目录（建议使用绝对路径）。
- **include_dirs**: 编译时需要包含的头文件目录（列表，可包含多个路径）。
- **defines**: 编译时需要定义的宏（列表）。
- **compiler**: 编译器的路径或命令（例如 `gcc`）。
- **source_files**: 源代码文件的匹配模式（支持通配符，如 `"**/*.c"`）。

### 配置文件示例

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

## ❓ 常见问题 (FAQ)

### 1. 如何指定头文件包含目录 (`include_dirs`)？

你可以在配置文件中手动指定要包含的目录，或者在生成模板时使用 `-i` 选项来自动包含所有子目录。

### 2. 如何查看生成的命令？

使用 `-v` 选项启用详细模式，可以看到工具执行过程和生成的命令的详细信息。

### 3. 如何生成自定义的配置文件？

使用 `-g` 选项生成模板文件，然后根据你的项目需求进行修改。

## 🤝 贡献

如果你有任何建议或问题，欢迎提交 Issue 或 Pull Request。

## 📜 许可证

本项目基于 MIT 许可证开源。更多信息请参阅 [LICENSE](LICENSE) 文件。
