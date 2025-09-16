#!/usr/bin/env python3
"""
使用第三方API接口爬取小红书今日热搜数据
基于顺为数据API: https://api.itapi.cn/doc/85

使用方法:
1. 注册顺为数据账号获取API密钥
2. 设置环境变量 XIAOHONGSHU_API_KEY 或直接在代码中填入
3. 运行脚本: python crawl_today_with_api.py
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from crawler.api_crawler import create_api_crawler
from utils.data_saver import DataSaver
from utils.analysis import analyze_hot_search_data
from utils.report_generator import generate_html_report


def main():
    """主函数"""
    print("🕷️  小红书今日热搜爬虫启动 (API接口版)...")
    
    # 获取API密钥
    api_key = os.getenv('XIAOHONGSHU_API_KEY')
    if not api_key:
        print("❌ 未设置API密钥")
        print("请设置环境变量 XIAOHONGSHU_API_KEY")
        print("获取API密钥方法:")
        print("1. 访问 https://api.itapi.cn/doc/85")
        print("2. 注册账号并获取API密钥")
        print("3. 设置环境变量: export XIAOHONGSHU_API_KEY=你的密钥")
        return 1
    
    try:
        # 创建爬虫
        print("正在创建API爬虫...")
        crawler = create_api_crawler(api_key)
        
        # 爬取数据
        print("正在爬取今日热搜数据...")
        result = crawler.crawl_hot_search()
        
        if not result or result.total == 0:
            print("❌ 获取热搜数据失败")
            return 1
        
        print(f"✅ 成功获取 {result.total} 条热搜数据")
        
        # 保存原始数据
        today = datetime.now().strftime("%Y-%m-%d")
        data_filename = f"xiaohongshu_hot_search_{today}"
        
        # 创建数据保存器并设置新的目录结构
        saver = DataSaver()
        
        # 创建会话目录结构: ymd/time/
        ymd = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M")
        session_dir = saver.create_session_directory(ymd, time_str)
        
        print(f"📁 创建输出目录: {session_dir}")
        
        # 保存为JSON格式到crawl_data子目录
        json_path = saver.save_json(result, f"{data_filename}.json", save_to_crawl_data=True)
        if json_path:
            print(f"📄 JSON数据已保存到: {json_path}")
        
        # 保存为CSV格式到crawl_data子目录
        csv_path = saver.save_csv(result, f"{data_filename}.csv", save_to_crawl_data=True)
        if csv_path:
            print(f"📊 CSV数据已保存到: {csv_path}")
        
        # 数据分析
        print("正在分析热搜数据...")
        analysis_result = analyze_hot_search_data(result)
        
        if analysis_result:
            print("✅ 数据分析完成")
            print(f"📈 平均热度: {analysis_result.get('avg_heat', 0):,.0f}")
            print(f"🔥 最高热度: {analysis_result.get('max_heat', 0):,.0f}")
            print(f"📊 分类数量: {len(analysis_result.get('categories', {}))}")
        else:
            print("⚠️  数据分析失败")
        
        # 生成HTML报告
        print("正在生成分析报告...")
        report_path = generate_html_report(
            result, 
            analysis_result, 
            "simple_analysis.html",
            output_dir=session_dir
        )
        
        if report_path:
            print(f"📋 分析报告已生成: {report_path}")
        else:
            print("⚠️  报告生成失败")
        
        # 显示前10条热搜
        print("\n📈 今日热搜榜 TOP 10:")
        print("-" * 50)
        for item in result.get_top_n(10):
            print(f"{item.rank:2d}. {item.word}")
            if item.heat > 0:
                print(f"    🔥 热度: {item.heat:,}")
            if hasattr(item, 'category') and item.category:
                print(f"    🏷️  分类: {item.category}")
            print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        return 1
    finally:
        if 'crawler' in locals():
            crawler.close()
        print("\n✨ 爬虫任务结束")


if __name__ == "__main__":
    exit(main())