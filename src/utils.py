"""
Utility functions for Code2Markdown converter.
"""
import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import fnmatch


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """获取文件的详细信息."""
    try:
        stat_info = file_path.stat()
        return {
            'size': stat_info.st_size,
            'modified': datetime.fromtimestamp(stat_info.st_mtime),
            'created': datetime.fromtimestamp(stat_info.st_ctime),
            'is_readonly': not (stat_info.st_mode & stat.S_IWRITE)
        }
    except (OSError, IOError):
        return {
            'size': 0,
            'modified': datetime.now(),
            'created': datetime.now(),
            'is_readonly': False
        }


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    if i == 0:
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.1f} {size_names[i]}"


def should_ignore_file(file_path: Path, ignore_patterns: set) -> bool:
    """检查文件是否应该被忽略."""
    file_name = file_path.name
    
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    
    return False


def should_ignore_dir(dir_path: Path, ignore_patterns: set) -> bool:
    """检查目录是否应该被忽略."""
    dir_name = dir_path.name
    return dir_name in ignore_patterns


def read_file_safely(file_path: Path, max_size: int = 1024 * 1024) -> Optional[str]:
    """安全读取文件内容，支持多种编码格式."""
    try:
        file_info = get_file_info(file_path)
        
        if file_info['size'] > max_size:
            return f"[文件过大 ({format_file_size(file_info['size'])}), 跳过显示内容]"
        
        # 尝试多种编码格式
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    content = f.read()
                # 清理内容中的控制字符和无效字符
                content = clean_text_content(content)
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # 如果所有编码都失败，使用utf-8并忽略错误
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            content = clean_text_content(content)
            
        return content
        
    except (OSError, IOError) as e:
        return f"[无法读取文件: {str(e)}]"


def clean_text_content(content: str) -> str:
    """清理文本内容中的无效字符."""
    if not content:
        return content
    
    import re
    
    # 移除控制字符，但保留常用的空白字符（空格、制表符、换行符）
    content = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', content)
    
    # 处理常见的编码问题导致的乱码模式
    replacements = {
        'ƣ': '函数名：',
        'ܣ': '功能：', 
        'ڲ': '参数：',
        'ڲ': '返回值：'
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    return content


def generate_tree_structure(root_path: Path, ignore_dirs: set, ignore_files: set, 
                          max_depth: int = 10, current_depth: int = 0) -> List[str]:
    """生成目录树结构."""
    if current_depth >= max_depth:
        return ["[目录层次过深，已截断]"]
    
    tree_lines = []
    
    try:
        items = []
        if root_path.exists() and root_path.is_dir():
            for item in root_path.iterdir():
                if item.is_dir() and not should_ignore_dir(item, ignore_dirs):
                    items.append((item, True))
                elif item.is_file() and not should_ignore_file(item, ignore_files):
                    items.append((item, False))
        
        items.sort(key=lambda x: (not x[1], x[0].name.lower()))
        
        for i, (item, is_dir) in enumerate(items):
            is_last = i == len(items) - 1
            prefix = "└── " if is_last else "├── "
            
            if is_dir:
                tree_lines.append(f"{prefix}{item.name}/")
                
                # 递归处理子目录
                child_prefix = "    " if is_last else "│   "
                child_lines = generate_tree_structure(
                    item, ignore_dirs, ignore_files, max_depth, current_depth + 1
                )
                
                for line in child_lines:
                    tree_lines.append(child_prefix + line)
            else:
                tree_lines.append(f"{prefix}{item.name}")
    
    except (OSError, PermissionError):
        tree_lines.append("[无法访问目录]")
    
    return tree_lines


def extract_project_name_from_path(path: Path) -> str:
    """从路径中提取项目名称."""
    # 通常项目名称是最深层的有意义的目录名
    parts = path.parts
    
    # 跳过根目录和可能的时间戳目录
    meaningful_parts = []
    for part in reversed(parts):
        if not part.startswith('.') and part not in ['Code', 'Markdown']:
            meaningful_parts.append(part)
        if len(meaningful_parts) >= 2:
            break
    
    # 返回最具体的项目名称
    if meaningful_parts:
        return meaningful_parts[0]
    
    return path.name


def normalize_project_name(name: str) -> str:
    """标准化项目名称，用于目录和文件命名."""
    # 移除时间戳后缀
    import re
    normalized = re.sub(r'_\d{8}$', '', name)
    return normalized


def ensure_directory(path: Path) -> None:
    """确保目录存在，如果不存在则创建."""
    path.mkdir(parents=True, exist_ok=True)