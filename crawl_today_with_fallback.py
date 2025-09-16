#!/usr/bin/env python3
"""
带Playwright兜底机制的小红书今日热搜爬虫
当requests方法失败时，会自动使用Playwright浏览器模拟
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from crawler.crawler_with_fallback import create_crawler_with_fallback
from utils.data_saver import DataSaver


def main():
    """主函数"""
    print("🕷️  小红书今日热搜爬虫启动 (带Playwright兜底)...")
    
    # 创建带兜底机制的爬虫
    crawler = create_crawler_with_fallback()
    
    try:
        # 获取今日热搜
        print("正在爬取今日热搜数据...")
        result = crawler.crawl_hot_search()
        
        if not result:
            print("❌ 获取热搜数据失败")
            return 1
        
        print(f"✅ 成功获取 {result.total} 条热搜数据")
        
        # 保存数据
        saver = DataSaver()
        today = datetime.now().strftime("%Y%m%d")
        
        # 保存JSON格式
        json_file = saver.save_json(result, f"xiaohongshu_hot_search_{today}.json")
        print(f"📁 JSON数据已保存: {json_file}")
        
        # 保存CSV格式
        csv_file = saver.save_csv(result, f"xiaohongshu_hot_search_{today}.csv")
        print(f"📁 CSV数据已保存: {csv_file}")
        
        # 显示前10条热搜
        print("\n📈 今日小红书热搜TOP10:")
        print("-" * 50)
        for i, item in enumerate(result.get_top_n(10), 1):
            print(f"{i:2d}. {item.word}")
            print(f"    🔥 热度: {item.heat:,}")
            print(f"    🔗 链接: {item.url}")
            print()
        
        # 生成简单的文本报告
        report_file = Path("output") / f"hot_search_report_{today}.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"小红书热搜报告 - {datetime.now().strftime('%Y年%m月%d日')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"总热搜词条数: {result.total}\n\n")
            f.write("TOP10热搜词条:\n")
            f.write("-" * 30 + "\n")
            for i, item in enumerate(result.get_top_n(10), 1):
                f.write(f"{i}. {item.word} (热度: {item.heat:,})\n")
        
        print(f"📄 文本报告已生成: {report_file}")
        print("\n🎉 爬虫任务完成！")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        crawler.close()


if __name__ == "__main__":
    sys.exit(main())