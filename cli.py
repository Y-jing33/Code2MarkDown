"""
Command Line Interface for Code2Markdown converter.
"""
import argparse
import sys
from pathlib import Path
from src.config import Config
from src.code2md import create_converter


def main():
    """CLI主函数."""
    parser = argparse.ArgumentParser(
        description="Convert code projects to structured Markdown documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                          # 转换所有项目
  python cli.py --project SC92F7003      # 转换特定项目
  python cli.py --code-dir MyCode        # 指定代码目录
  python cli.py --no-content             # 不包含文件内容
        """
    )
    
    parser.add_argument(
        "--code-dir",
        type=str,
        default="Code",
        help="代码源目录 (默认: Code)"
    )
    
    parser.add_argument(
        "--markdown-dir", 
        type=str,
        default="Markdown",
        help="Markdown输出目录 (默认: Markdown)"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="转换特定项目（项目名称或路径模式）"
    )
    
    parser.add_argument(
        "--no-content",
        action="store_true",
        help="不包含文件内容，仅生成项目结构和统计信息"
    )
    
    parser.add_argument(
        "--no-stats",
        action="store_true", 
        help="不包含文件统计信息"
    )
    
    parser.add_argument(
        "--no-structure",
        action="store_true",
        help="不包含项目结构树"
    )
    
    parser.add_argument(
        "--max-file-size",
        type=str,
        default="1MB",
        help="最大文件大小限制 (默认: 1MB)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    try:
        # 解析文件大小
        max_size = parse_size(args.max_file_size)
        
        # 创建配置
        config = Config(
            code_base_dir=Path(args.code_dir),
            markdown_base_dir=Path(args.markdown_dir),
            include_file_content=not args.no_content,
            include_file_stats=not args.no_stats,
            include_project_structure=not args.no_structure,
            max_file_size=max_size
        )
        
        # 验证目录
        if not (Path.cwd() / config.code_base_dir).exists():
            print(f"❌ 代码目录不存在: {config.code_base_dir}")
            return 1
        
        # 创建转换器
        converter = create_converter(config)
        
        if args.verbose:
            print(f"📁 代码目录: {config.code_base_dir}")
            print(f"📄 输出目录: {config.markdown_base_dir}")
            print(f"📊 包含内容: {config.include_file_content}")
            print(f"📈 包含统计: {config.include_file_stats}")
            print(f"🌳 包含结构: {config.include_project_structure}")
            print(f"📏 最大文件: {args.max_file_size}")
            print("=" * 50)
        
        if args.project:
            # 转换特定项目
            success = convert_specific_project(converter, args.project, args.verbose)
            return 0 if success else 1
        else:
            # 转换所有项目
            success_count, total_count = converter.convert_all_projects()
            
            # 生成索引
            if success_count > 0:
                projects = []
                for project_path in converter.discover_projects():
                    project_info = converter.analyze_project(project_path)
                    projects.append(project_info)
                
                converter.generate_index(projects)
            
            # 输出结果
            print("=" * 50)
            print(f"✅ 转换完成: {success_count}/{total_count} 个项目")
            
            if success_count < total_count:
                print(f"⚠️  {total_count - success_count} 个项目转换失败")
                return 1
            
            return 0
            
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def convert_specific_project(converter, project_pattern: str, verbose: bool = False) -> bool:
    """转换特定项目."""
    projects = converter.discover_projects()
    
    # 查找匹配的项目
    matched_projects = []
    for project_path in projects:
        if (project_pattern.lower() in project_path.name.lower() or 
            project_pattern.lower() in str(project_path).lower()):
            matched_projects.append(project_path)
    
    if not matched_projects:
        print(f"❌ 未找到匹配的项目: {project_pattern}")
        if verbose:
            print("可用项目:")
            for project_path in projects:
                print(f"  - {project_path.name}")
        return False
    
    if len(matched_projects) > 1:
        print(f"⚠️  找到多个匹配的项目:")
        for project_path in matched_projects:
            print(f"  - {project_path.name}")
        print("请使用更具体的项目名称")
        return False
    
    # 转换匹配的项目
    project_path = matched_projects[0]
    success = converter.convert_project(project_path)
    
    if success:
        print(f"✅ 项目转换成功: {project_path.name}")
    else:
        print(f"❌ 项目转换失败: {project_path.name}")
    
    return success


def parse_size(size_str: str) -> int:
    """解析大小字符串为字节数."""
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'K': 1024, 'KB': 1024,
        'M': 1024*1024, 'MB': 1024*1024,
        'G': 1024*1024*1024, 'GB': 1024*1024*1024
    }
    
    # 提取数字和单位
    import re
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([A-Z]*)$', size_str)
    if not match:
        raise ValueError(f"无效的大小格式: {size_str}")
    
    number = float(match.group(1))
    unit = match.group(2) or 'B'
    
    if unit not in multipliers:
        raise ValueError(f"无效的大小单位: {unit}")
    
    return int(number * multipliers[unit])


if __name__ == "__main__":
    sys.exit(main())