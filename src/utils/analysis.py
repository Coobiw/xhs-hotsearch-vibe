"""
热搜数据分析工具
"""
from typing import Dict, Any, Optional, List
from collections import Counter
from statistics import mean, median
from loguru import logger

from crawler.models import HotSearchResult, HotSearchItem


def analyze_hot_search_data(result: HotSearchResult) -> Optional[Dict[str, Any]]:
    """分析热搜数据"""
    try:
        if not result or result.total == 0:
            logger.warning("没有数据可供分析")
            return None
        
        items = result.items
        
        # 基础统计
        total_items = len(items)
        heat_values = [item.heat for item in items if item.heat > 0]
        
        # 热度统计
        avg_heat = mean(heat_values) if heat_values else 0
        max_heat = max(heat_values) if heat_values else 0
        min_heat = min(heat_values) if heat_values else 0
        median_heat = median(heat_values) if heat_values else 0
        
        # 分类统计
        categories = [item.category for item in items if item.category]
        category_count = Counter(categories)
        
        # 关键词长度统计
        word_lengths = [len(item.word) for item in items]
        avg_length = mean(word_lengths) if word_lengths else 0
        
        # 标签统计
        all_tags = []
        for item in items:
            all_tags.extend(item.tags)
        tag_count = Counter(all_tags)
        
        # 热门词汇分析（简单的词频统计）
        word_freq = Counter()
        for item in items:
            words = item.word.split()
            word_freq.update(words)
        
        analysis_result = {
            'total_items': total_items,
            'heat_stats': {
                'avg_heat': avg_heat,
                'max_heat': max_heat,
                'min_heat': min_heat,
                'median_heat': median_heat
            },
            'categories': dict(category_count),
            'avg_word_length': avg_length,
            'top_tags': dict(tag_count.most_common(10)),
            'top_words': dict(word_freq.most_common(20)),
            'crawl_time': result.crawl_time.isoformat()
        }
        
        logger.info(f"数据分析完成: {total_items} 条数据")
        logger.info(f"平均热度: {avg_heat:,.0f}, 最高热度: {max_heat:,.0f}")
        logger.info(f"分类数量: {len(category_count)}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"数据分析失败: {e}")
        return None


def categorize_hot_search_items(items: List[HotSearchItem]) -> Dict[str, List[HotSearchItem]]:
    """按分类对热搜词条进行分组"""
    try:
        categories = {}
        
        for item in items:
            category = item.category or '其他'
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        return categories
        
    except Exception as e:
        logger.error(f"分类失败: {e}")
        return {}


def extract_keywords_from_items(items: List[HotSearchItem]) -> List[str]:
    """从热搜词条中提取关键词"""
    try:
        keywords = []
        
        for item in items:
            # 简单的关键词提取：按空格分割，过滤短词
            words = item.word.split()
            for word in words:
                word = word.strip('，。！？、：；""''（）【】《》')
                if len(word) >= 2:  # 只保留长度大于等于2的词
                    keywords.append(word)
        
        # 返回不重复的关键词列表
        return list(set(keywords))
        
    except Exception as e:
        logger.error(f"关键词提取失败: {e}")
        return []


def generate_trend_analysis(current_items: List[HotSearchItem], 
                           previous_items: List[HotSearchItem]) -> Dict[str, Any]:
    """生成趋势分析（对比当前和之前的数据）"""
    try:
        if not previous_items:
            return {'status': 'no_previous_data'}
        
        # 创建当前和之前的词条映射
        current_words = {item.word: item for item in current_items}
        previous_words = {item.word: item for item in previous_items}
        
        # 新增词条
        new_words = []
        for word, item in current_words.items():
            if word not in previous_words:
                new_words.append(item)
        
        # 消失的词条
        removed_words = []
        for word, item in previous_words.items():
            if word not in current_words:
                removed_words.append(item)
        
        # 排名变化的词条
        rank_changes = []
        for word, current_item in current_words.items():
            if word in previous_words:
                previous_item = previous_words[word]
                rank_change = previous_item.rank - current_item.rank
                if rank_change != 0:
                    rank_changes.append({
                        'word': word,
                        'current_rank': current_item.rank,
                        'previous_rank': previous_item.rank,
                        'change': rank_change
                    })
        
        return {
            'new_items': len(new_words),
            'removed_items': len(removed_words),
            'rank_changes': rank_changes,
            'new_words_list': [item.word for item in new_words[:10]],  # 只显示前10个
            'removed_words_list': [item.word for item in removed_words[:10]]
        }
        
    except Exception as e:
        logger.error(f"趋势分析失败: {e}")
        return {'status': 'error', 'message': str(e)}