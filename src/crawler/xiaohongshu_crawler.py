"""
小红书热搜爬虫实现
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from .base_crawler import BaseCrawler
from .models import HotSearchResult, HotSearchItem, CrawlerConfig


class XiaohongshuCrawler(BaseCrawler):
    """小红书热搜爬虫"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__(config)
        self.hot_search_url = config.hot_search_url
        self.limit = config.limit
    
    def _parse_hot_search_data(self, data: Dict[str, Any]) -> Optional[HotSearchResult]:
        """解析热搜数据"""
        try:
            result = HotSearchResult()
            
            # 检查数据结构
            if not data or 'data' not in data:
                logger.error("返回数据格式错误")
                return None
            
            items_data = data.get('data', [])
            if not items_data:
                logger.warning("未获取到热搜数据")
                return result
            
            logger.info(f"获取到 {len(items_data)} 条热搜数据")
            
            for idx, item_data in enumerate(items_data[:self.limit]):
                try:
                    # 提取热搜词条信息
                    word = item_data.get('word', '')
                    heat = item_data.get('heat', 0)
                    url = item_data.get('url', '')
                    
                    if not word:
                        logger.warning(f"第 {idx + 1} 条数据缺少词条信息，跳过")
                        continue
                    
                    # 创建热搜词条对象
                    hot_item = HotSearchItem(
                        word=word,
                        heat=heat,
                        rank=idx + 1,
                        url=url,
                        created_at=datetime.now()
                    )
                    
                    result.add_item(hot_item)
                    logger.debug(f"解析热搜词条: {word} (热度: {heat})")
                    
                except Exception as e:
                    logger.error(f"解析第 {idx + 1} 条热搜数据失败: {e}")
                    continue
            
            logger.info(f"成功解析 {result.total} 条热搜词条")
            return result
            
        except Exception as e:
            logger.error(f"解析热搜数据失败: {e}")
            return None
    
    def crawl_hot_search(self) -> Optional[HotSearchResult]:
        """爬取小红书热搜数据"""
        try:
            logger.info("开始爬取小红书热搜数据")
            
            # 准备请求参数
            params = {
                'limit': self.limit,
                'sort': 'heat'
            }
            
            # 发送请求
            response_data = self._make_request(self.hot_search_url, params)
            if not response_data:
                logger.error("获取热搜数据失败")
                return None
            
            # 解析数据
            result = self._parse_hot_search_data(response_data)
            if result:
                logger.success(f"成功获取 {result.total} 条热搜数据")
            else:
                logger.error("解析热搜数据失败")
            
            return result
            
        except Exception as e:
            logger.error(f"爬取热搜数据过程出错: {e}")
            return None
    
    def save_raw_data(self, data: Dict[str, Any], filename: str):
        """保存原始数据（调试用）"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"原始数据已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存原始数据失败: {e}")


def create_default_crawler() -> XiaohongshuCrawler:
    """创建默认配置的小红书爬虫"""
    config = CrawlerConfig(
        hot_search_url="https://www.xiaohongshu.com",
        timeout=30,
        max_retries=3,
        request_delay=3,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        limit=50
    )
    
    return XiaohongshuCrawler(config)


if __name__ == "__main__":
    # 测试爬虫
    crawler = create_default_crawler()
    try:
        result = crawler.crawl_hot_search()
        if result:
            print(f"成功获取 {result.total} 条热搜数据")
            for item in result.get_top_n(10):
                print(f"{item.rank}. {item.word} - 热度: {item.heat}")
        else:
            print("爬取失败")
    finally:
        crawler.close()