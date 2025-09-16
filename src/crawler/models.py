"""
数据模型定义
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HotSearchItem(BaseModel):
    """热搜词条数据模型"""
    word: str = Field(..., description="热搜词条")
    heat: int = Field(..., description="热度值")
    rank: int = Field(..., description="排名")
    url: str = Field(..., description="搜索链接")
    category: Optional[str] = Field(None, description="分类")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HotSearchResult(BaseModel):
    """热搜结果数据模型"""
    items: List[HotSearchItem] = Field(default_factory=list, description="热搜词条列表")
    total: int = Field(0, description="总数")
    crawl_time: datetime = Field(default_factory=datetime.now, description="爬取时间")
    source: str = Field("xiaohongshu", description="数据来源")
    
    def add_item(self, item: HotSearchItem):
        """添加热搜词条"""
        self.items.append(item)
        self.total = len(self.items)
    
    def get_top_n(self, n: int) -> List[HotSearchItem]:
        """获取前N个热搜词条"""
        return self.items[:n]
    
    def filter_by_category(self, category: str) -> List[HotSearchItem]:
        """按分类筛选"""
        return [item for item in self.items if item.category == category]


class CrawlerConfig(BaseModel):
    """爬虫配置模型"""
    hot_search_url: str = Field(..., description="热搜接口地址")
    timeout: int = Field(30, description="请求超时时间")
    max_retries: int = Field(3, description="重试次数")
    request_delay: int = Field(3, description="请求间隔时间")
    user_agent: str = Field(..., description="用户代理")
    limit: int = Field(50, description="获取热搜数量")
    use_playwright: bool = Field(False, description="是否使用Playwright")
    browser_type: str = Field("chromium", description="浏览器类型")
    headless: bool = Field(True, description="是否无头模式")
    
    
class AntiBotConfig(BaseModel):
    """反爬配置模型"""
    use_proxy: bool = Field(False, description="是否使用代理")
    use_playwright: bool = Field(True, description="是否启用Playwright")
    browser_type: str = Field("chromium", description="浏览器类型")
    headless: bool = Field(True, description="是否无头模式")
    proxies: List[str] = Field(default_factory=list, description="代理列表")