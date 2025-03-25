"""
测试爬虫功能的简单脚本
"""
import asyncio
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_crawler.log'),
        logging.StreamHandler()
    ]
)

# 导入自定义模块
from config import Config
from database import Database
from scraper import ZhihuHotQuestionScraper

# 确保截图目录存在
screenshot_dir = "screenshots"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# 初始化配置和数据库
config = Config()
config.set('visible_mode', True)  # 设置为可视模式
db = Database(config.get('database_path', 'database/zhihu_hot_questions.db'))

# 爬虫任务
async def test_scrape():
    """测试爬取任务"""
    try:
        logging.info(f"开始执行测试爬取任务: {datetime.now()}")
        
        # 创建爬虫实例
        scraper = ZhihuHotQuestionScraper(config)
        
        # 执行爬取
        questions = await scraper.scrape()
        
        # 保存到数据库
        if questions:
            saved_count = db.save_questions(questions)
            logging.info(f"成功保存 {saved_count} 个问题到数据库")
            
            # 输出部分数据
            print("\n爬取到的问题示例:")
            for i, q in enumerate(questions[:5]):
                print(f"{i+1}. {q['title']} (热力值: {q.get('hot_value', 'N/A')})")
        else:
            logging.warning("没有获取到问题数据")
        
        return len(questions)
    except Exception as e:
        logging.error(f"爬取任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    try:
        # 执行爬取
        count = asyncio.run(test_scrape())
        logging.info(f"爬取完成，获取到 {count} 个问题")
    except KeyboardInterrupt:
        logging.info("应用被用户中断")
    except Exception as e:
        logging.error(f"应用运行出错: {e}")
        import traceback
        traceback.print_exc() 