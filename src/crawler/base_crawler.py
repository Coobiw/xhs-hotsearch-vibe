"""
基础爬虫类
"""
import time
import random
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from loguru import logger
from fake_useragent import UserAgent

from .models import HotSearchResult, CrawlerConfig


class BaseCrawler(ABC):
    """基础爬虫类"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()
    
    def _setup_session(self):
        """设置会话配置"""
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
            'Origin': 'https://www.xiaohongshu.com'
        })
        
        # 设置请求超时
        self.session.timeout = self.config.timeout
    
    def _add_random_delay(self):
        """添加随机延迟"""
        delay = random.uniform(self.config.request_delay, self.config.request_delay + 2)
        logger.debug(f"等待 {delay:.2f} 秒")
        time.sleep(delay)
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """发送HTTP请求"""
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"第 {attempt + 1} 次请求: {url}")
                self._add_random_delay()
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    logger.error(f"所有重试均失败: {url}")
                    return None
                
                # 指数退避
                wait_time = (2 ** attempt) + random.uniform(1, 3)
                logger.info(f"等待 {wait_time:.2f} 秒后重试")
                time.sleep(wait_time)
        
        return None
    
    @abstractmethod
    def crawl_hot_search(self) -> Optional[HotSearchResult]:
        """爬取热搜数据"""
        pass
    
    def close(self):
        """关闭爬虫"""
        if hasattr(self.session, 'close'):
            self.session.close()
        logger.info("爬虫已关闭")