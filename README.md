# 小红书每日热搜爬虫
p.s.: 整个项目由Claude Code + Kimi-K2-0905在10-20分钟内完成，我个人没写一行代码...

## 📋 项目简介

这是一个用于爬取小红书每日热搜词条的Python项目，支持数据分析和HTML报告生成。由于小红书严格的反爬机制，项目采用第三方API接口获取热搜数据，确保稳定可靠的数据获取。

## ✨ 功能特性

- **🔥 热搜数据获取**：通过API接口获取小红书实时热搜榜
- **📊 数据分析**：热度统计、分类分析、关键词提取
- **📋 HTML报告**：美观的响应式网页报告
- **🆕 深度分析报告**：结合网络搜索的智能话题解读和趋势预测
- **💾 多格式导出**：支持JSON和CSV格式数据导出
- **🛡️ 错误处理**：完善的异常处理和重试机制

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 相关依赖包（见requirements.txt）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/Coobiw/xhs-hotsearch-vibe
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **获取API密钥**
   - 访问 [顺为数据API](https://api.itapi.cn/doc/85)
   - 注册账号（免费用户每天100次调用）
   - 获取API密钥

4. **设置环境变量**
```bash
export XIAOHONGSHU_API_KEY=你的密钥
```

5. **运行爬虫**
```bash
python crawl_today_with_api.py
```

## 📁 项目结构

```
xiaohongshu_crawler/
├── src/
│   ├── crawler/
│   │   ├── api_crawler.py          # API接口爬虫
│   │   ├── xiaohongshu_crawler.py  # 原始网页爬虫
│   │   ├── crawler_with_fallback.py # 带Playwright兜底的爬虫
│   │   ├── base_crawler.py         # 爬虫基类
│   │   └── models.py               # 数据模型
│   └── utils/
│       ├── data_saver.py          # 数据保存工具
│       ├── analysis.py            # 数据分析工具
│       ├── report_generator.py    # HTML报告生成器
│       └── logger.py              # 日志配置
├── tasks/                         # 任务记录
│   └── TODO.md                    # 项目进展跟踪
├── output/                        # 输出目录（按日期组织）
│   └── 20250917/                  # 示例：2025年9月17日数据
│       └── 0346/                  # 时间戳目录
│           ├── crawl_data/        # 原始爬取数据
│           │   ├── xiaohongshu_hot_search_2025-09-17.json
│           │   └── xiaohongshu_hot_search_2025-09-17.csv
│           └── further_analysis.html  # 🆕 深度分析报告
├── crawl_today_with_api.py        # API爬虫启动脚本
├── crawl_today_with_fallback.py   # 原始爬虫启动脚本
├── CLAUDE.md                      # 🆕 项目说明和进展记录
├── requirements.txt               # 项目依赖
└── README.md                      # 项目文档
```

## 📊 输出结果

### 数据文件
- **JSON格式**：完整的热搜数据，包含排名、词条、热度、分类等信息
- **CSV格式**：便于Excel或其他工具进行数据分析

### HTML报告内容
- 📈 热搜榜单TOP 20
- 📊 热度统计分析（平均、最高、最低热度）
- 🏷️ 分类分布统计
- 📈 热门关键词提取
- 🎨 现代化的响应式设计

### 🆕 深度分析报告（新增）
- 🔍 **智能分类**：自动将热搜词分为科技、娱乐、社会、生活等类别
- 📊 **趋势洞察**：基于数据的社会文化现象分析
- 🌐 **背景研究**：结合网络搜索提供热点话题深度解读
- 💡 **预测分析**：基于当前数据预测未来发展趋势
- 📱 **响应式设计**：支持移动端查看的交互式报告

## 🔧 配置选项

### API爬虫配置
可以在 `src/crawler/api_crawler.py` 中调整以下参数：
- `timeout`: 请求超时时间（默认30秒）
- `limit`: 获取热搜数量（默认50条）

### 数据保存配置
可以在 `src/utils/data_saver.py` 中配置：
- `data_dir`: 数据保存目录（默认"data"）
- `output_dir`: 输出目录（默认"output"）

## ⚠️ 注意事项

1. **API限制**：免费用户每天100次调用，请勿频繁请求
2. **数据更新**：热搜数据约5-10分钟更新一次
3. **网络要求**：需要稳定的网络连接访问API接口

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 🔗 相关链接

- [顺为数据API文档](https://api.itapi.cn/doc/85)
- [小红书官网](https://www.xiaohongshu.com)