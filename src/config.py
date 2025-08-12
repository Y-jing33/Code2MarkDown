"""
Configuration module for Code2Markdown converter.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Set, List


@dataclass
class Config:
    """Configuration settings for Code2Markdown converter."""
    
    # 基础路径配置
    code_base_dir: Path = Path("Code")
    markdown_base_dir: Path = Path("Markdown")
    
    # 代码文件扩展名配置
    code_extensions: Set[str] = None
    
    # 项目文件扩展名配置（不包含在代码统计中）
    project_extensions: Set[str] = None
    
    # 忽略的文件和目录
    ignore_files: Set[str] = None
    ignore_dirs: Set[str] = None
    
    # 文件大小限制（字节）
    max_file_size: int = 1024 * 1024  # 1MB
    
    # Markdown模板配置
    include_file_content: bool = True
    include_file_stats: bool = True
    include_project_structure: bool = True
    
    def __post_init__(self):
        """初始化默认配置值."""
        if self.code_extensions is None:
            self.code_extensions = {
                '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx',
                '.py', '.java', '.js', '.ts', '.cs',
                '.go', '.rs', '.php', '.rb', '.swift',
                '.kt', '.scala', '.clj', '.hs', '.ml',
                '.asm', '.s', '.a51'
            }
        
        if self.project_extensions is None:
            self.project_extensions = {
                '.uvproj', '.uvopt', '.uvgui', '.sln', '.vcxproj',
                '.pro', '.qbs', '.cmake', '.mk', '.makefile',
                '.json', '.xml', '.yml', '.yaml', '.toml',
                '.cfg', '.conf', '.ini'
            }
        
        if self.ignore_files is None:
            self.ignore_files = {
                '.DS_Store', 'Thumbs.db', '.gitignore',
                '__pycache__', '*.pyc', '*.pyo', '*.pyd',
                '.vscode', '.idea', '.vs'
            }
        
        if self.ignore_dirs is None:
            self.ignore_dirs = {
                '__pycache__', '.git', '.svn', '.hg',
                'node_modules', '.vscode', '.idea', '.vs',
                'bin', 'obj', 'build', 'dist', 'target'
            }


# 语言映射配置
LANGUAGE_MAPPING: Dict[str, str] = {
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.py': 'python',
    '.java': 'java',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.clj': 'clojure',
    '.hs': 'haskell',
    '.ml': 'ocaml',
    '.asm': 'assembly',
    '.s': 'assembly',
    '.a51': 'assembly'
}


def get_language_for_extension(ext: str) -> str:
    """根据文件扩展名获取语言标识符."""
    return LANGUAGE_MAPPING.get(ext.lower(), 'text')