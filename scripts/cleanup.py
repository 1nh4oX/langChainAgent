"""
项目清理脚本
删除旧文件和作业相关内容，保留干净的项目结构
"""

import os
import shutil
from pathlib import Path

def cleanup():
    """清理项目目录"""
    print("="*60)
    print("🧹 开始清理项目目录...")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    # 要删除的文件列表
    files_to_delete = [
        # 旧的主程序文件（已被 src/ 替代）
        "main.py",
        "stock_tools.py",
        "collect_news.py",
        "test_agent.py",
        "simple_test.py",
        
        # 作业相关文件
        "作业报告.md",
        "作业提交-打印版.txt",
        "getFreeApi.md",
        
        # 数据文件（已采集完成）
        "stock_news_*.csv",
        "stock_news_*.json",
        "stock_news_*.xlsx",
        "news_report_*.txt",
        "test_report_*.txt",
        "simple_test_result_*.txt",
        
        # 临时文件
        "README_NEW.md",  # 会重命名为 README.md
    ]
    
    # 要删除的目录
    dirs_to_delete = [
        "old_files",  # 如果存在的话
    ]
    
    deleted_count = 0
    kept_count = 0
    
    print("\n📝 将要删除的文件:")
    print("-"*60)
    
    # 删除文件
    for pattern in files_to_delete:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                print(f"  ❌ {file_path.name}")
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"     错误: {e}")
    
    # 删除目录
    for dir_name in dirs_to_delete:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ❌ {dir_name}/ (目录)")
            try:
                shutil.rmtree(dir_path)
                deleted_count += 1
            except Exception as e:
                print(f"     错误: {e}")
    
    # 重命名 README_NEW.md 为 README.md
    readme_new = project_root / "README_NEW.md"
    readme_old = project_root / "README.md"
    
    if readme_new.exists():
        print("\n📝 重命名 README...")
        try:
            if readme_old.exists():
                readme_old.unlink()
            readme_new.rename(readme_old)
            print("  ✅ README_NEW.md → README.md")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    # 显示保留的重要文件
    print("\n" + "="*60)
    print("✅ 保留的项目结构:")
    print("="*60)
    
    important_items = [
        "src/",
        "scripts/",
        "tests/",
        "data/",
        "docs/",
        "examples/",
        "ui/",
        "app.py",
        "setup.py",
        "requirements.txt",
        ".gitignore",
        ".env.example",
        "LICENSE",
        "README.md",
        "CONTRIBUTING.md",
        "MIGRATION_GUIDE.md",
    ]
    
    for item in important_items:
        item_path = project_root / item
        if item_path.exists():
            if item_path.is_dir():
                print(f"  📁 {item}")
            else:
                print(f"  📄 {item}")
            kept_count += 1
    
    print("\n" + "="*60)
    print("🎉 清理完成！")
    print("="*60)
    print(f"❌ 删除: {deleted_count} 个文件/目录")
    print(f"✅ 保留: {kept_count} 个重要文件")
    print("\n💡 提示:")
    print("- 项目现在使用新的模块化结构")
    print("- 运行主程序: python app.py")
    print("- 查看文档: README.md, MIGRATION_GUIDE.md")
    print("- 开始开发: 参考 CONTRIBUTING.md")


if __name__ == "__main__":
    try:
        print("\n⚠️  警告: 此操作将删除旧文件和作业相关内容！")
        print("删除的文件包括:")
        print("  - 旧的主程序 (main.py, stock_tools.py 等)")
        print("  - 作业文件 (作业报告.md, 作业提交-打印版.txt 等)")
        print("  - 数据文件 (*.csv, *.json, *.xlsx)")
        print("  - 测试报告文件")
        print()
        
        response = input("确认清理？(yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            cleanup()
        else:
            print("\n❌ 已取消清理")
            
    except KeyboardInterrupt:
        print("\n\n❌ 已取消清理")


