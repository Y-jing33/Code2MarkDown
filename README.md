# Code2Markdown

一个强大的代码项目转Markdown文档工具，专门设计用于将复杂的代码项目结构转换为结构化的Markdown文档。

## 功能特性

- 🔍 **自动项目发现**: 自动扫描Code目录中的所有项目
- 📁 **智能结构识别**: 支持多层嵌套的项目目录结构
- 📊 **详细统计信息**: 自动统计代码文件、头文件、项目文件等
- 🌳 **目录树生成**: 自动生成美观的项目结构树
- 📝 **代码内容展示**: 支持多种编程语言的语法高亮
- ⚡ **批量处理**: 一次性处理多个项目
- 🎯 **可配置**: 丰富的配置选项适应不同需求
- 📋 **索引生成**: 自动生成项目索引文件

## 支持的文件类型

### 编程语言
- C/C++ (`.c`, `.h`, `.cpp`, `.hpp`, `.cc`, `.cxx`)
- Assembly (`.asm`, `.s`, `.a51`)
- Python (`.py`)
- Java (`.java`)
- JavaScript/TypeScript (`.js`, `.ts`)
- C# (`.cs`)
- Go (`.go`)
- Rust (`.rs`)
- 以及更多...

### 项目文件
- Keil uVision (`.uvproj`, `.uvopt`, `.uvgui`)
- Visual Studio (`.sln`, `.vcxproj`)
- 配置文件 (`.json`, `.xml`, `.yml`, `.toml`)

## 快速开始

### 基本使用

```bash
# 转换所有项目
python main.py

# 或者使用CLI
python cli.py
```

### 高级用法

```bash
# 转换特定项目
python cli.py --project SC92F7003

# 自定义目录
python cli.py --code-dir MyCode --markdown-dir MyDocs

# 只生成结构，不包含文件内容
python cli.py --no-content

# 限制文件大小
python cli.py --max-file-size 500KB

# 显示详细信息
python cli.py --verbose
```

## 项目结构

```
Code2Markdown/
├── Code/                      # 源代码目录
│   ├── Project1_20240126/
│   │   └── Project1/
│   └── Project2_20240126/
│       └── Project2/
├── Markdown/                  # 输出文档目录
│   ├── INDEX.md              # 项目索引
│   ├── Project1.md           # 项目1文档
│   └── Project2.md           # 项目2文档
├── src/                      # 核心代码
│   ├── __init__.py
│   ├── code2md.py           # 主转换器
│   ├── config.py            # 配置管理
│   └── utils.py             # 工具函数
├── main.py                   # 简单运行入口
├── cli.py                    # 命令行接口
└── pyproject.toml           # 项目配置
```

## 配置选项

通过修改 `src/config.py` 中的 `Config` 类来自定义行为：

```python
config = Config(
    code_base_dir=Path("Code"),           # 代码源目录
    markdown_base_dir=Path("Markdown"),   # 输出目录
    include_file_content=True,            # 是否包含文件内容
    include_file_stats=True,              # 是否包含统计信息
    include_project_structure=True,       # 是否包含目录结构
    max_file_size=1024*1024              # 最大文件大小(1MB)
)
```

## 输出格式

每个项目会生成一个以项目名称命名的.md文件（如`SC92F7003_Demo_Code.md`），包含以下内容：

1. **项目信息**: 名称、生成时间、源路径
2. **项目结构**: 美观的目录树展示
3. **文件统计**: 各类文件的数量统计
4. **文件详情**: 每个代码文件的详细信息和内容

所有Markdown文件直接放在`Markdown`目录中，无子文件夹结构，便于管理和访问。

## 依赖管理

本项目使用 `uv` 进行依赖管理：

```bash
# 安装依赖
uv sync

# 运行项目
uv run python main.py

# 或
uv run python cli.py
```

## 扩展性

系统设计为高度可扩展：

- **添加新语言支持**: 修改 `config.py` 中的语言映射
- **自定义文件过滤**: 调整忽略规则和文件类型
- **修改输出格式**: 自定义Markdown模板生成逻辑
- **添加新功能**: 通过继承转换器类实现自定义行为

## 许可证

MIT License

## 贡献

欢迎提交问题和改进建议！