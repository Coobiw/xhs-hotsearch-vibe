"""
HTML报告生成器
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from crawler.models import HotSearchResult


def generate_html_report(result: HotSearchResult, 
                        analysis_result: Optional[Dict[str, Any]] = None,
                        output_filename: str = "simple_analysis.html",
                        output_dir: Optional[Path] = None) -> Optional[str]:
    """生成HTML格式的分析报告
    
    Args:
        result: 热搜数据
        analysis_result: 分析结果
        output_filename: 输出文件名，默认为simple_analysis.html
        output_dir: 输出目录，如果为None则在当前目录
    """
    try:
        if not result or result.total == 0:
            logger.warning("没有数据可供生成报告")
            return None
        
        # 生成报告内容
        html_content = _generate_html_content(result, analysis_result)
        
        # 确定输出路径
        if output_dir:
            output_path = output_dir / output_filename
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path(output_filename)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML报告已生成: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"生成HTML报告失败: {e}")
        return None


def _generate_html_content(result: HotSearchResult, analysis_result: Optional[Dict[str, Any]]) -> str:
    """生成HTML内容"""
    now = datetime.now()
    
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书热搜分析报告 - {now.strftime('%Y年%m月%d日')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border-radius: 15px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .stat-card p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #ff6b6b;
        }}
        
        .section h2 {{
            color: #2d3436;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #ff6b6b;
            padding-bottom: 10px;
        }}
        
        .hot-list {{
            display: grid;
            gap: 15px;
        }}
        
        .hot-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #ff6b6b;
            transition: all 0.3s ease;
        }}
        
        .hot-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .hot-item .rank {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 15px;
        }}
        
        .hot-item .word {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 8px;
        }}
        
        .hot-item .meta {{
            color: #636e72;
            font-size: 0.9em;
        }}
        
        .hot-item .heat {{
            color: #e17055;
            font-weight: bold;
        }}
        
        .category-tag {{
            display: inline-block;
            background: #74b9ff;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #2d3436;
            color: white;
            border-radius: 15px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 小红书热搜分析报告</h1>
            <p>{now.strftime('%Y年%m月%d日 %H:%M')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{result.total}</h3>
                <p>热搜词条总数</p>
            </div>
            """
    
    # 如果有分析结果，添加统计信息
    if analysis_result:
        heat_stats = analysis_result.get('heat_stats', {})
        categories = analysis_result.get('categories', {})
        
        html_template += f"""
            <div class="stat-card">
                <h3>{heat_stats.get('max_heat', 0):,.0f}</h3>
                <p>最高热度</p>
            </div>
            
            <div class="stat-card">
                <h3>{heat_stats.get('avg_heat', 0):,.0f}</h3>
                <p>平均热度</p>
            </div>
            
            <div class="stat-card">
                <h3>{len(categories)}</h3>
                <p>分类数量</p>
            </div>
        """
    
    html_template += f"""
        </div>
        
        <div class="section">
            <h2>📈 今日热搜榜 TOP {min(20, result.total)}</h2>
            <div class="hot-list">
    """
    
    # 添加热搜词条
    for item in result.get_top_n(20):
        heat_info = f"🔥 热度: {item.heat:,}" if item.heat > 0 else ""
        category_tag = f"<span class='category-tag'>{item.category}</span>" if hasattr(item, 'category') and item.category else ""
        # 构建小红书搜索URL
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={item.word}"
        
        html_template += f"""
                <div class="hot-item" onclick="window.open('{search_url}', '_blank')" style="cursor: pointer;">
                    <span class="rank">{item.rank}</span>
                    <div style="display: inline-block; vertical-align: middle;">
                        <div class="word">{item.word}{category_tag}</div>
                        <div class="meta">
                            {heat_info}
                            <span style="margin-left: 15px;">📅 {item.created_at.strftime('%H:%M')}</span>
                        </div>
                    </div>
                </div>
        """
    
    html_template += f"""
            </div>
        </div>
        
        """
    
    # 如果有分析结果，添加详细分析
    if analysis_result:
        html_template += f"""
        <div class="section">
            <h2>📊 数据分析</h2>
            
            <div class="chart-container">
                <h3>热度统计</h3>
                <ul>
                    <li>平均热度: {analysis_result.get('heat_stats', {}).get('avg_heat', 0):,.0f}</li>
                    <li>最高热度: {analysis_result.get('heat_stats', {}).get('max_heat', 0):,.0f}</li>
                    <li>最低热度: {analysis_result.get('heat_stats', {}).get('min_heat', 0):,.0f}</li>
                    <li>中位数热度: {analysis_result.get('heat_stats', {}).get('median_heat', 0):,.0f}</li>
                </ul>
            </div>
            
            <div class="chart-container">
                <h3>分类分布</h3>
                <ul>
        """
        
        categories = analysis_result.get('categories', {})
        for category, count in categories.items():
            html_template += f"<li>{category}: {count} 个词条</li>"
        
        html_template += f"""
                </ul>
            </div>
            
            <div class="chart-container">
                <h3>热门关键词</h3>
                <p>平均词条长度: {analysis_result.get('avg_word_length', 0):.1f} 个字符</p>
            </div>
        </div>
        """
    
    html_template += f"""
        <div class="footer">
            <p>📊 报告生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🤖 由小红书热搜爬虫自动生成</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html_template.strip()