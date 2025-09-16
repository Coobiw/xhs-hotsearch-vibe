"""
数据保存工具
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger

try:
    from ..crawler.models import HotSearchResult, HotSearchItem
except ImportError:
    # 直接运行时的导入处理
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from crawler.models import HotSearchResult, HotSearchItem


class DataSaver:
    """数据保存器"""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "output", 
                 base_output_dir: str = "output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.base_output_dir = Path(base_output_dir)
        self.current_session_dir = None
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保基础目录存在"""
        self.data_dir.mkdir(exist_ok=True)
        self.base_output_dir.mkdir(exist_ok=True)
    
    def create_session_directory(self, ymd: str = None, time_str: str = None) -> Path:
        """创建会话目录结构: ymd/time/"""
        if not ymd:
            ymd = datetime.now().strftime("%Y%m%d")
        if not time_str:
            time_str = datetime.now().strftime("%H%M")
        
        session_dir = self.base_output_dir / ymd / time_str
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (session_dir / "crawl_data").mkdir(exist_ok=True)
        
        self.current_session_dir = session_dir
        self.output_dir = session_dir  # 更新输出目录
        
        logger.info(f"创建会话目录: {session_dir}")
        return session_dir
    
    def save_json(self, data: HotSearchResult, filename: Optional[str] = None, 
                  save_to_crawl_data: bool = True) -> str:
        """保存为JSON格式
        
        Args:
            data: 热搜数据
            filename: 文件名，如果为None则自动生成
            save_to_crawl_data: 是否保存到crawl_data子目录
        """
        if not filename:
            today = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xiaohongshu_hot_search_{today}.json"
        
        # 确定保存路径
        if save_to_crawl_data and self.current_session_dir:
            file_path = self.current_session_dir / "crawl_data" / filename
        else:
            file_path = self.data_dir / filename
        
        try:
            # 转换为可序列化的格式
            data_dict = {
                "total": data.total,
                "crawl_time": data.crawl_time.isoformat(),
                "source": data.source,
                "items": []
            }
            
            for item in data.items:
                item_dict = {
                    "word": item.word,
                    "heat": item.heat,
                    "rank": item.rank,
                    "url": item.url,
                    "category": item.category,
                    "tags": item.tags,
                    "created_at": item.created_at.isoformat()
                }
                data_dict["items"].append(item_dict)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存为JSON: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存JSON失败: {e}")
            raise
    
    def save_csv(self, data: HotSearchResult, filename: Optional[str] = None, 
                 save_to_crawl_data: bool = False) -> str:
        """保存为CSV格式
        
        Args:
            data: 热搜数据
            filename: 文件名，如果为None则自动生成
            save_to_crawl_data: 是否保存到crawl_data子目录
        """
        if not filename:
            today = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xiaohongshu_hot_search_{today}.csv"
        
        # 确定保存路径
        if save_to_crawl_data and self.current_session_dir:
            file_path = self.current_session_dir / "crawl_data" / filename
        else:
            file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow(['排名', '热搜词条', '热度', '分类', '标签', '链接', '创建时间'])
                
                # 写入数据
                for item in data.items:
                    writer.writerow([
                        item.rank,
                        item.word,
                        item.heat,
                        item.category or '',
                        ','.join(item.tags) if item.tags else '',
                        item.url,
                        item.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    ])
            
            logger.info(f"数据已保存为CSV: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"保存CSV失败: {e}")
            raise
    
    def load_json(self, filename: str) -> Optional[HotSearchResult]:
        """从JSON文件加载数据"""
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            
            result = HotSearchResult(
                total=data_dict.get('total', 0),
                crawl_time=datetime.fromisoformat(data_dict.get('crawl_time', datetime.now().isoformat())),
                source=data_dict.get('source', 'xiaohongshu')
            )
            
            for item_data in data_dict.get('items', []):
                item = HotSearchItem(
                    word=item_data['word'],
                    heat=item_data['heat'],
                    rank=item_data['rank'],
                    url=item_data['url'],
                    category=item_data.get('category'),
                    tags=item_data.get('tags', []),
                    created_at=datetime.fromisoformat(item_data.get('created_at', datetime.now().isoformat()))
                )
                result.add_item(item)
            
            logger.info(f"成功从JSON加载数据: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"加载JSON失败: {e}")
            return None
    
    def get_latest_files(self, count: int = 5) -> List[str]:
        """获取最新的数据文件列表"""
        try:
            json_files = list(self.data_dir.glob("*.json"))
            csv_files = list(self.data_dir.glob("*.csv"))
            
            all_files = json_files + csv_files
            all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return [str(f) for f in all_files[:count]]
            
        except Exception as e:
            logger.error(f"获取文件列表失败: {e}")
            return []


def main():
    """测试数据保存器"""
    saver = DataSaver()
    
    # 创建测试数据
    from datetime import datetime
    result = HotSearchResult()
    
    # 添加一些测试数据
    test_items = [
        ("测试热搜1", 10000, 1),
        ("测试热搜2", 8000, 2),
        ("测试热搜3", 6000, 3),
    ]
    
    for word, heat, rank in test_items:
        item = HotSearchItem(
            word=word,
            heat=heat,
            rank=rank,
            url=f"https://www.xiaohongshu.com/search_result?keyword={word}",
            category="测试分类",
            tags=["测试标签1", "测试标签2"],
            created_at=datetime.now()
        )
        result.add_item(item)
    
    # 测试保存功能
    print("正在测试数据保存功能...")
    
    json_file = saver.save_json(result)
    print(f"JSON文件: {json_file}")
    
    csv_file = saver.save_csv(result)
    print(f"CSV文件: {csv_file}")
    
    # 测试加载功能
    loaded_result = saver.load_json(Path(json_file).name)
    if loaded_result:
        print(f"成功加载数据，共 {loaded_result.total} 条记录")
    
    print("测试完成！")


if __name__ == "__main__":
    main()