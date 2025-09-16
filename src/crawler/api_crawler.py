"""
使用第三方API接口的小红书热搜爬虫
基于顺为数据API: https://api.itapi.cn/api/hotnews/xiaohongshu
"""
import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from .models import HotSearchResult, HotSearchItem, CrawlerConfig


class XiaohongshuApiCrawler:
    """使用API接口的小红书热搜爬虫"""
    
    def __init__(self, api_key: str, config: Optional[CrawlerConfig] = None):
        self.api_key = api_key
        self.api_url = "https://api.itapi.cn/api/hotnews/xiaohongshu"
        self.config = config or CrawlerConfig()
        
    def _make_api_request(self) -> Optional[Dict[str, Any]]:
        """调用API接口获取数据"""
        try:
            logger.info("正在调用小红书热搜API接口")
            
            params = {
                'key': self.api_key
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=self.config.timeout or 30
            )
            
            if response.status_code != 200:
                logger.error(f"API请求失败: {response.status_code}")
                return None
                
            data = response.json()
            
            # 检查API返回状态
            if data.get('code') != 200:
                logger.error(f"API返回错误: {data.get('msg', '未知错误')}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"API返回数据解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            return None
    
    def _parse_api_data(self, data: Dict[str, Any]) -> Optional[HotSearchResult]:
        """解析API返回的数据"""
        try:
            result = HotSearchResult()
            
            # 获取热搜列表数据
            hot_list = data.get('data', [])
            if not hot_list:
                logger.warning("API未返回热搜数据")
                return result
            
            logger.info(f"API返回了 {len(hot_list)} 条热搜数据")
            
            for idx, item_data in enumerate(hot_list[:self.config.limit]):
                try:
                    # 提取热搜词条信息
                    word = item_data.get('name', '')
                    rank = int(item_data.get('rank', idx + 1))
                    heat_str = item_data.get('viewnum', '0')
                    url = item_data.get('url', '')
                    word_type = item_data.get('word_type', '热')
                    
                    if not word:
                        logger.warning(f"第 {idx + 1} 条数据缺少词条信息，跳过")
                        continue
                    
                    # 解析热度值（将类似"1100.9w"的字符串转换为数字）
                    heat = self._parse_heat_value(heat_str)
                    
                    # 创建热搜词条对象
                    hot_item = HotSearchItem(
                        word=word,
                        heat=heat,
                        rank=rank,
                        url=url,
                        created_at=datetime.now(),
                        category=word_type  # 使用word_type作为分类
                    )
                    
                    result.add_item(hot_item)
                    logger.debug(f"解析热搜词条: {word} (热度: {heat_str})")
                    
                except Exception as e:
                    logger.error(f"解析第 {idx + 1} 条热搜数据失败: {e}")
                    continue
            
            logger.info(f"成功解析 {result.total} 条热搜词条")
            return result
            
        except Exception as e:
            logger.error(f"解析API数据失败: {e}")
            return None
    
    def _parse_heat_value(self, heat_str: str) -> int:
        """解析热度值字符串"""
        try:
            if not heat_str:
                return 0
            
            # 处理类似"1100.9万"或"1100.9w"的格式
            heat_str = heat_str.lower().strip()
            
            # 移除可能的空格和逗号
            heat_str = heat_str.replace(' ', '').replace(',', '')
            
            if '万' in heat_str or 'w' in heat_str:
                # 处理中文"万"和英文"w"
                num_str = heat_str.replace('万', '').replace('w', '')
                return int(float(num_str) * 10000)
            elif '千' in heat_str or 'k' in heat_str:
                # 处理中文"千"和英文"k"
                num_str = heat_str.replace('千', '').replace('k', '')
                return int(float(num_str) * 1000)
            else:
                # 纯数字，可能是已经转换过的
                return int(float(heat_str))
                
        except (ValueError, TypeError):
            logger.warning(f"无法解析热度值: {heat_str}")
            return 0
    
    def crawl_hot_search(self) -> Optional[HotSearchResult]:
        """爬取小红书热搜数据"""
        try:
            logger.info("开始通过API获取小红书热搜数据")
            
            # 调用API
            api_data = self._make_api_request()
            if not api_data:
                logger.error("API调用失败")
                return None
            
            # 解析数据
            result = self._parse_api_data(api_data)
            if result:
                logger.success(f"成功获取 {result.total} 条热搜数据")
            else:
                logger.error("解析API数据失败")
            
            return result
            
        except Exception as e:
            logger.error(f"通过API获取热搜数据失败: {e}")
            return None
    
    def close(self):
        """关闭爬虫（API爬虫不需要特殊清理）"""
        logger.info("API爬虫已关闭")


def create_api_crawler(api_key: str = None) -> XiaohongshuApiCrawler:
    """创建API接口爬虫
    
    Args:
        api_key: API密钥，如果不提供则尝试从环境变量XIAOHONGSHU_API_KEY获取
    """
    if not api_key:
        import os
        api_key = os.getenv('XIAOHONGSHU_API_KEY')
    
    if not api_key:
        raise ValueError("需要提供API密钥，可通过参数或环境变量XIAOHONGSHU_API_KEY设置")
    
    config = CrawlerConfig(
        hot_search_url="https://api.itapi.cn/api/hotnews/xiaohongshu",
        user_agent="XiaohongshuApiCrawler/1.0",
        timeout=30,
        limit=50
    )
    
    return XiaohongshuApiCrawler(api_key, config)


if __name__ == "__main__":
    # 测试API爬虫
    import os
    
    # 从环境变量获取API密钥
    api_key = os.getenv('XIAOHONGSHU_API_KEY')
    if not api_key:
        print("请先设置环境变量 XIAOHONGSHU_API_KEY")
        print("如果没有API密钥，可以注册顺为数据获取: https://api.itapi.cn/doc/85")
        exit(1)
    
    try:
        crawler = create_api_crawler(api_key)
        result = crawler.crawl_hot_search()
        
        if result:
            print(f"成功获取 {result.total} 条热搜数据")
            for item in result.get_top_n(10):
                print(f"{item.rank}. {item.word} - 热度: {item.heat}")
        else:
            print("获取热搜数据失败")
            
    except Exception as e:
        print(f"运行失败: {e}")
    finally:
        crawler.close()