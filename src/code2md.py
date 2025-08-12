"""
Main Code2Markdown converter module.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .config import Config, get_language_for_extension
from .utils import (
    get_file_info, format_file_size, should_ignore_file, should_ignore_dir,
    read_file_safely, generate_tree_structure, extract_project_name_from_path,
    normalize_project_name, ensure_directory
)


@dataclass
class FileStats:
    """文件统计信息."""
    code_files: int = 0
    header_files: int = 0
    project_files: int = 0
    other_files: int = 0
    total_size: int = 0


@dataclass
class ProjectInfo:
    """项目信息."""
    name: str
    source_path: Path
    target_path: Path
    generated_time: datetime
    stats: FileStats


class Code2MarkdownConverter:
    """Code2Markdown 转换器主类."""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化转换器."""
        self.config = config or Config()
        self.root_path = Path.cwd()
        
    def discover_projects(self) -> List[Path]:
        """发现所有需要转换的项目."""
        code_dir = self.root_path / self.config.code_base_dir
        
        if not code_dir.exists():
            raise FileNotFoundError(f"代码目录不存在: {code_dir}")
        
        projects = []
        
        # 遍历Code目录，寻找项目
        for item in code_dir.iterdir():
            if item.is_dir() and not should_ignore_dir(item, self.config.ignore_dirs):
                # 检查是否是包含项目的时间戳目录
                project_dirs = self._find_project_directories(item)
                projects.extend(project_dirs)
        
        return projects
    
    def _find_project_directories(self, base_dir: Path) -> List[Path]:
        """在给定目录中查找项目目录."""
        project_dirs = []
        
        # 直接检查当前目录是否是项目目录
        if self._is_project_directory(base_dir):
            project_dirs.append(base_dir)
        else:
            # 递归查找子目录中的项目
            for subdir in base_dir.iterdir():
                if subdir.is_dir() and not should_ignore_dir(subdir, self.config.ignore_dirs):
                    if self._is_project_directory(subdir):
                        project_dirs.append(subdir)
                    else:
                        # 最多递归两层
                        sub_projects = self._find_project_directories(subdir)
                        if sub_projects:
                            project_dirs.extend(sub_projects)
        
        return project_dirs
    
    def _is_project_directory(self, path: Path) -> bool:
        """判断目录是否是一个项目目录."""
        # 检查是否包含代码文件或项目文件
        has_code_files = False
        has_project_files = False
        
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    ext = item.suffix.lower()
                    if ext in self.config.code_extensions:
                        has_code_files = True
                    elif ext in self.config.project_extensions:
                        has_project_files = True
                    
                    if has_code_files or has_project_files:
                        return True
        except (OSError, PermissionError):
            pass
        
        return False
    
    def analyze_project(self, project_path: Path) -> ProjectInfo:
        """分析项目并生成项目信息."""
        stats = FileStats()
        
        # 遍历项目文件
        for item in project_path.rglob('*'):
            if item.is_file() and not should_ignore_file(item, self.config.ignore_files):
                file_info = get_file_info(item)
                stats.total_size += file_info['size']
                
                ext = item.suffix.lower()
                if ext in self.config.code_extensions:
                    if ext in {'.h', '.hpp', '.hh'}:
                        stats.header_files += 1
                    else:
                        stats.code_files += 1
                elif ext in self.config.project_extensions:
                    stats.project_files += 1
                else:
                    stats.other_files += 1
        
        project_name = extract_project_name_from_path(project_path)
        normalized_name = normalize_project_name(project_name)
        
        # 直接生成.md文件，而不是创建子目录
        target_file = self.root_path / self.config.markdown_base_dir / f"{normalized_name}.md"
        
        return ProjectInfo(
            name=project_name,
            source_path=project_path,
            target_path=target_file,  # 现在是文件路径而不是目录路径
            generated_time=datetime.now(),
            stats=stats
        )
    
    def convert_project(self, project_path: Path) -> bool:
        """转换单个项目为Markdown文档."""
        try:
            print(f"正在转换项目: {project_path}")
            
            # 分析项目
            project_info = self.analyze_project(project_path)
            
            # 确保输出目录存在（target_path现在是文件路径）
            ensure_directory(project_info.target_path.parent)
            
            # 生成Markdown文档
            markdown_content = self._generate_markdown(project_info)
            
            # 直接写入以项目名命名的.md文件
            with open(project_info.target_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ 转换完成: {project_info.target_path}")
            return True
            
        except Exception as e:
            print(f"❌ 转换失败 {project_path}: {str(e)}")
            return False
    
    def _generate_markdown(self, project_info: ProjectInfo) -> str:
        """生成Markdown内容."""
        lines = []
        
        # 标题
        lines.append(f"# {project_info.name}")
        lines.append("")
        
        # 项目信息
        lines.append("## 项目信息")
        lines.append(f"- **项目名称**: {project_info.name}")
        lines.append(f"- **生成时间**: {project_info.generated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **项目路径**: `{project_info.source_path}`")
        lines.append("")
        
        # 项目结构
        if self.config.include_project_structure:
            lines.append("## 项目结构")
            lines.append("")
            lines.append("```")
            
            tree_lines = generate_tree_structure(
                project_info.source_path, 
                self.config.ignore_dirs, 
                self.config.ignore_files
            )
            
            if tree_lines:
                lines.append(f"{project_info.name}/")
                for tree_line in tree_lines:
                    if tree_line.strip():
                        lines.append(tree_line)
            
            lines.append("```")
            lines.append("")
        
        # 文件统计
        if self.config.include_file_stats:
            lines.append("## 文件统计")
            lines.append(f"- 源代码文件: {project_info.stats.code_files}")
            lines.append(f"- 头文件: {project_info.stats.header_files}")
            lines.append(f"- 项目文件: {project_info.stats.project_files}")
            lines.append(f"- 其他文件: {project_info.stats.other_files}")
            lines.append("")
        
        # 文件内容
        if self.config.include_file_content:
            file_sections = self._generate_file_sections(project_info.source_path)
            lines.extend(file_sections)
        
        return "\n".join(lines)
    
    def _generate_file_sections(self, project_path: Path) -> List[str]:
        """生成文件内容部分."""
        sections = []
        
        # 收集所有代码文件
        code_files = []
        for item in project_path.rglob('*'):
            if (item.is_file() and 
                item.suffix.lower() in self.config.code_extensions and
                not should_ignore_file(item, self.config.ignore_files)):
                code_files.append(item)
        
        # 按文件名排序
        code_files.sort(key=lambda x: x.name.lower())
        
        for file_path in code_files:
            sections.extend(self._generate_file_section(file_path, project_path))
        
        return sections
    
    def _generate_file_section(self, file_path: Path, project_root: Path) -> List[str]:
        """生成单个文件的Markdown部分."""
        lines = []
        
        # 计算相对路径
        try:
            relative_path = file_path.relative_to(project_root)
        except ValueError:
            relative_path = file_path
        
        # 文件信息
        file_info = get_file_info(file_path)
        
        # 文件标题
        lines.append(f"## {file_path.name}")
        lines.append("")
        
        # 文件基本信息
        lines.append(f"**文件路径**: `{relative_path}`  ")
        lines.append(f"**文件类型**: {get_language_for_extension(file_path.suffix).upper()}  ")
        lines.append(f"**文件大小**: {format_file_size(file_info['size'])}  ")
        lines.append(f"**最后修改**: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}  ")
        lines.append("")
        
        # 文件内容
        content = read_file_safely(file_path, self.config.max_file_size)
        if content:
            language = get_language_for_extension(file_path.suffix)
            
            lines.append("### 文件内容")
            lines.append("")
            lines.append(f"```{language}")
            lines.append(content)
            lines.append("```")
            lines.append("")
        
        return lines
    
    def convert_all_projects(self) -> Tuple[int, int]:
        """转换所有项目."""
        projects = self.discover_projects()
        
        if not projects:
            print("❌ 未发现任何项目")
            return 0, 0
        
        print(f"📁 发现 {len(projects)} 个项目")
        
        success_count = 0
        total_count = len(projects)
        
        for project_path in projects:
            if self.convert_project(project_path):
                success_count += 1
        
        return success_count, total_count
    
    def generate_index(self, projects: List[ProjectInfo]) -> None:
        """生成索引文件."""
        markdown_dir = self.root_path / self.config.markdown_base_dir
        index_path = markdown_dir / "INDEX.md"
        
        lines = []
        lines.append("# Code2Markdown 项目索引")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**项目总数**: {len(projects)}")
        lines.append("")
        
        if projects:
            lines.append("## 项目列表")
            lines.append("")
            
            for project in sorted(projects, key=lambda p: p.name):
                # 现在直接链接到.md文件而不是子目录中的README.md
                md_filename = f"{normalize_project_name(project.name)}.md"
                lines.append(f"- [{project.name}]({md_filename})")
            
            lines.append("")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        print(f"📄 生成索引文件: {index_path}")


def create_converter(config: Optional[Config] = None) -> Code2MarkdownConverter:
    """创建转换器实例."""
    return Code2MarkdownConverter(config)