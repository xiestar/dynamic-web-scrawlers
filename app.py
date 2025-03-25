import os
import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# 导入自定义模块
from config import Config
from database import Database
from scraper import ZhihuHotQuestionScraper
from web import create_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zhihu_crawler.log'),
        logging.StreamHandler()
    ]
)

# 初始化配置和数据库
config = Config()
db = Database(config.get('database_path', 'database/zhihu_hot_questions.db'))

# 创建Flask应用
app = create_app(config, db)

# 定义爬虫任务
async def crawl_task():
    """定时爬取任务"""
    try:
        logging.info(f"开始执行定时爬取任务: {datetime.now()}")
        
        # 创建爬虫实例
        scraper = ZhihuHotQuestionScraper(config)
        
        # 执行爬取
        questions = await scraper.scrape()
        
        # 保存到数据库
        if questions:
            saved_count = db.save_questions(questions)
            logging.info(f"成功保存 {saved_count} 个问题到数据库")
        else:
            logging.warning("没有获取到问题数据")
        
    except Exception as e:
        logging.error(f"爬取任务执行失败: {e}")

# 创建调度器
scheduler = BackgroundScheduler()

def start_scheduler():
    """启动定时任务"""
    try:
        # 添加爬虫任务，按配置的间隔定时执行
        interval_seconds = config.get('scrape_interval', 3600)  # 默认1小时
        
        scheduler.add_job(
            lambda: asyncio.run(crawl_task()),
            'interval', 
            seconds=interval_seconds,
            id='zhihu_crawl_job',
            replace_existing=True
        )
        
        # 添加立即执行一次的任务
        scheduler.add_job(
            lambda: asyncio.run(crawl_task()),
            'date',
            run_date=datetime.now(),
            id='zhihu_crawl_once'
        )
        
        # 启动调度器
        if not scheduler.running:
            scheduler.start()
            logging.info(f"调度器已启动，爬虫任务将每 {interval_seconds} 秒执行一次")
    except Exception as e:
        logging.error(f"启动调度器失败: {e}")

# 处理应用退出时清理资源
def cleanup():
    """清理资源"""
    if scheduler.running:
        scheduler.shutdown()
        logging.info("调度器已关闭")

if __name__ == '__main__':
    try:
        # 启动调度器
        start_scheduler()
        
        # 启动Web应用
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logging.info("应用被用户中断")
    except Exception as e:
        logging.error(f"应用运行出错: {e}")
    finally:
        # 清理资源
        cleanup() 