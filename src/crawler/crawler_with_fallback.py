"""
带Playwright兜底机制的小红书爬虫
"""
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright未安装，浏览器兜底机制不可用")

from .xiaohongshu_crawler import XiaohongshuCrawler
from .models import HotSearchResult, HotSearchItem, CrawlerConfig


class XiaohongshuCrawlerWithFallback(XiaohongshuCrawler):
    """带Playwright兜底机制的小红书爬虫"""
    
    def __init__(self, config: CrawlerConfig):
        super().__init__(config)
        self.use_playwright = config.use_playwright and PLAYWRIGHT_AVAILABLE
        self.browser = None
        self.playwright = None
    
    def _setup_playwright(self):
        """设置Playwright浏览器"""
        if not self.use_playwright:
            return False
        
        try:
            logger.info("正在启动Playwright浏览器...")
            self.playwright = sync_playwright().start()
            
            # 启动浏览器
            browser_type = getattr(self.playwright, self.config.browser_type, self.playwright.chromium)
            self.browser = browser_type.launch(
                headless=self.config.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            logger.success("Playwright浏览器启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动Playwright浏览器失败: {e}")
            self.use_playwright = False
            return False
    
    def _crawl_with_playwright(self):
        """使用Playwright爬取数据"""
        if not self.browser:
            return None
        
        try:
            logger.info("使用Playwright爬取热搜数据")
            
            # 创建新页面
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.config.user_agent
            )
            
            page = context.new_page()
            
            # 设置页面超时
            page.set_default_timeout(self.config.timeout * 1000)
            
            # 访问热搜页面
            logger.info(f"访问页面: {self.hot_search_url}")
            page.goto(self.hot_search_url, wait_until='networkidle')
            
            # 等待页面加载
            time.sleep(5)
            
            # 尝试获取页面内容
            content = page.content()
            logger.info(f"页面内容长度: {len(content)} 字符")
            
            # 尝试从页面脚本中提取数据
            result = self._extract_data_from_page(page)
            
            # 关闭页面和上下文
            page.close()
            context.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Playwright爬取失败: {e}")
            return None
    
    def _extract_data_from_page(self, page):
        """从页面提取数据"""
        try:
            # 尝试多种方法提取数据
            
            # 方法1: 直接查找热搜词条元素
            result = HotSearchResult()
            
            # 尝试查找热搜词条
            hot_items = page.locator('[class*="hot-search"], [class*="trending"], [class*="hot"]')
            
            if hot_items.count() > 0:
                logger.info(f"找到 {hot_items.count()} 个可能的词条元素")
                
                for i in range(min(hot_items.count(), self.limit)):
                    try:
                        item = hot_items.nth(i)
                        
                        # 提取文本内容
                        text_content = item.text_content()
                        if text_content:
                            hot_item = HotSearchItem(
                                word=text_content.strip(),
                                heat=0,
                                rank=i + 1,
                                url="",
                                created_at=datetime.now()
                            )
                            result.add_item(hot_item)
                            logger.debug(f"提取词条: {text_content.strip()}")
                    
                    except Exception as e:
                        logger.warning(f"提取第 {i + 1} 个词条失败: {e}")
                        continue
            
            # 方法2: 尝试从window对象获取数据
            try:
                window_data = page.evaluate("""() => {
                    // 尝试从全局变量中获取数据
                    for (let key in window) {
                        if (key.includes('hot') || key.includes('trending') || key.includes('search')) {
                            let value = window[key];
                            if (typeof value === 'object' && value !== null) {
                                return value;
                            }
                        }
                    }
                    return null;
                }""")
                
                if window_data and isinstance(window_data, dict):
                    logger.info("从window对象获取到数据")
                    # 这里可以进一步解析window_data
                    
            except Exception as e:
                logger.debug(f"从window对象获取数据失败: {e}")
            
            # 方法3: 查找特定的脚本标签
            scripts = page.locator('script').element_handles()
            for script in scripts:
                try:
                    script_content = script.text_content()
                    if script_content and ('hot' in script_content.lower() or 'trending' in script_content.lower()):
                        logger.debug("找到可能包含数据的脚本")
                        # 这里可以进一步解析脚本内容
                        
                except Exception as e:
                    continue
            
            if result.total > 0:
                logger.success(f"Playwright成功提取 {result.total} 条数据")
                return result
            else:
                logger.warning("Playwright未提取到有效数据")
                return None
                
        except Exception as e:
            logger.error(f"页面数据提取失败: {e}")
            return None
    
    def crawl_hot_search(self):
        """爬取小红书热搜数据(带兜底机制)"""
        # 首先尝试使用requests方法
        logger.info("尝试使用requests方法获取数据")
        result = super().crawl_hot_search()
        
        if result and result.total > 0:
            logger.success("requests方法成功获取数据")
            return result
        
        # 如果requests失败，尝试使用Playwright
        if self.use_playwright:
            logger.info("requests方法失败，尝试使用Playwright兜底")
            
            # 设置Playwright
            if self._setup_playwright():
                result = self._crawl_with_playwright()
                
                if result and result.total > 0:
                    logger.success("Playwright兜底成功获取数据")
                else:
                    logger.error("Playwright兜底也未能获取数据")
                
                return result
            else:
                logger.error("Playwright设置失败，无法使用兜底机制")
        
        logger.error("所有方法均失败，无法获取热搜数据")
        return None
    
    def close(self):
        """关闭爬虫和浏览器"""
        super().close()
        
        if self.browser:
            try:
                self.browser.close()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
        
        if self.playwright:
            try:
                self.playwright.stop()
                logger.info("Playwright已停止")
            except Exception as e:
                logger.error(f"停止Playwright失败: {e}")


def create_crawler_with_fallback():
    """创建带兜底机制的爬虫"""
    config = CrawlerConfig(
        hot_search_url="https://www.xiaohongshu.com",
        timeout=30,
        max_retries=3,
        request_delay=3,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        limit=50,
        use_playwright=True,
        browser_type="chromium",
        headless=True
    )
    
    return XiaohongshuCrawlerWithFallback(config)


if __name__ == "__main__":
    # 测试带兜底机制的爬虫
    crawler = create_crawler_with_fallback()
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