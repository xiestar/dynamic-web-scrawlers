"""
知乎热点问题采集系统启动脚本
"""
import os
import logging
import asyncio
from datetime import datetime
import time
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zhihu_crawler.log'),
        logging.StreamHandler()
    ]
)

# 解析命令行参数
parser = argparse.ArgumentParser(description='知乎热点问题采集系统')
parser.add_argument('--scrape-only', action='store_true', help='只执行爬取，不启动Web服务')
parser.add_argument('--web-only', action='store_true', help='只启动Web服务，不执行爬取')
parser.add_argument('--port', type=int, default=5000, help='Web服务端口号')
parser.add_argument('--debug', action='store_true', help='启用调试模式')
parser.add_argument('--headless', action='store_false', dest='visible', default=True, 
                   help='以无头模式运行爬虫(默认为可视模式，便于人工验证)')
args = parser.parse_args()

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
db = Database(config.get('database_path', 'database/zhihu_hot_questions.db'))

# 将可视化模式参数添加到配置中
config.set('visible_mode', args.visible)

# 爬虫任务
async def scrape_task():
    """执行爬取任务"""
    try:
        logging.info(f"开始执行爬取任务: {datetime.now()}")
        logging.info(f"浏览器可视化模式: {'启用' if config.get('visible_mode') else '禁用'}")
        
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

# 启动Web服务
def start_web_server(port=5000, debug=False):
    """启动Web服务"""
    try:
        # 导入Web模块 (延迟导入避免循环依赖)
        from web import create_app
        
        # 创建Flask应用
        app = create_app(config, db)
        
        # 启动Web服务
        logging.info(f"启动Web服务，监听端口: {port}")
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logging.error(f"启动Web服务失败: {e}")

# 定时执行爬取任务
def schedule_scrape(interval_seconds=3600):
    """定时执行爬取任务"""
    while True:
        asyncio.run(scrape_task())
        logging.info(f"等待 {interval_seconds} 秒后再次执行爬取任务...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        # 根据命令行参数执行不同的操作
        if args.scrape_only:
            # 只执行一次爬取
            logging.info("只执行一次爬取任务")
            asyncio.run(scrape_task())
        elif args.web_only:
            # 只启动Web服务
            logging.info("只启动Web服务")
            start_web_server(port=args.port, debug=args.debug)
        else:
            # 先执行一次爬取
            count = asyncio.run(scrape_task())
            logging.info(f"初始爬取完成，获取到 {count} 个问题")
            
            # 启动Web服务
            import threading
            
            # 创建定时爬取线程
            interval = config.get('scrape_interval', 3600)
            scrape_thread = threading.Thread(
                target=schedule_scrape,
                args=(interval,),
                daemon=True
            )
            scrape_thread.start()
            
            # 启动Web服务（主线程）
            start_web_server(port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logging.info("应用被用户中断")
    except Exception as e:
        logging.error(f"应用运行出错: {e}")
        import traceback
        traceback.print_exc() 