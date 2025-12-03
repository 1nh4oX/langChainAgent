"""
Migration Script
迁移旧文件到新的目录结构

运行此脚本将旧的文件移动到适当的位置
"""

import os
import shutil
from pathlib import Path

def migrate():
    """迁移旧文件"""
    print("="*60)
    print("开始迁移旧文件...")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    # 定义迁移规则
    migrations = [
        # (源文件, 目标目录)
        ("stock_news_*.csv", "data/raw/"),
        ("stock_news_*.json", "data/raw/"),
        ("stock_news_*.xlsx", "data/raw/"),
        ("news_report_*.txt", "data/raw/"),
        ("test_report_*.txt", "data/raw/"),
        ("simple_test_result_*.txt", "data/raw/"),
        ("作业报告.md", "docs/"),
        ("作业提交-打印版.txt", "docs/"),
        ("getFreeApi.md", "docs/"),
    ]
    
    moved_count = 0
    skipped_count = 0
    
    for pattern, dest_dir in migrations:
        dest_path = project_root / dest_dir
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # 查找匹配的文件
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                try:
                    dest_file = dest_path / file_path.name
                    
                    # 如果目标文件已存在，添加时间戳
                    if dest_file.exists():
                        timestamp = file_path.stat().st_mtime
                        name, ext = os.path.splitext(file_path.name)
                        dest_file = dest_path / f"{name}_{int(timestamp)}{ext}"
                    
                    shutil.move(str(file_path), str(dest_file))
                    print(f"✅ 移动: {file_path.name} → {dest_dir}")
                    moved_count += 1
                    
                except Exception as e:
                    print(f"❌ 失败: {file_path.name} - {str(e)}")
                    skipped_count += 1
    
    # 创建备份目录并移动旧的主文件
    old_files_dir = project_root / "old_files"
    old_files_dir.mkdir(exist_ok=True)
    
    old_main_files = [
        "main.py",
        "stock_tools.py",
        "collect_news.py",
        "test_agent.py",
        "simple_test.py"
    ]
    
    print(f"\n" + "="*60)
    print("备份旧的主程序文件...")
    print("="*60)
    
    for filename in old_main_files:
        file_path = project_root / filename
        if file_path.exists():
            try:
                dest_file = old_files_dir / filename
                if not dest_file.exists():
                    shutil.copy2(str(file_path), str(dest_file))
                    print(f"✅ 备份: {filename} → old_files/")
                else:
                    print(f"⏭️  跳过: {filename} (已存在)")
                    skipped_count += 1
            except Exception as e:
                print(f"❌ 失败: {filename} - {str(e)}")
                skipped_count += 1
    
    print(f"\n" + "="*60)
    print("迁移完成！")
    print("="*60)
    print(f"✅ 成功移动: {moved_count} 个文件")
    print(f"⏭️  跳过: {skipped_count} 个文件")
    print("\n提示:")
    print("- 旧的主程序文件已备份到 old_files/ 目录")
    print("- 数据文件已移动到 data/raw/ 目录")
    print("- 文档文件已移动到 docs/ 目录")
    print("- 你可以删除 old_files/ 目录如果确认不再需要")


if __name__ == "__main__":
    try:
        response = input("确认迁移旧文件？这将移动和重命名一些文件。(y/n): ")
        if response.lower() in ['y', 'yes']:
            migrate()
        else:
            print("已取消迁移。")
    except KeyboardInterrupt:
        print("\n\n已取消迁移。")


