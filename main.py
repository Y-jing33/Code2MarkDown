"""
Code2Markdown - 代码项目转Markdown文档工具
"""
import sys
from pathlib import Path
from src.config import Config
from src.code2md import create_converter


def main():
    """主函数."""
    print("🚀 Code2Markdown 转换器")
    print("=" * 50)
    
    try:
        # 创建配置
        config = Config()
        
        # 验证目录结构
        if not (Path.cwd() / config.code_base_dir).exists():
            print(f"❌ 代码目录不存在: {config.code_base_dir}")
            print(f"   请确保在正确的工作目录中运行此脚本")
            return 1
        
        # 创建转换器
        converter = create_converter(config)
        
        # 转换所有项目
        success_count, total_count = converter.convert_all_projects()
        
        # 生成索引
        if success_count > 0:
            # 重新获取项目信息用于生成索引
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
        return 1


if __name__ == "__main__":
    sys.exit(main())
