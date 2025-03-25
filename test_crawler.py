import asyncio
import logging
import os
import pytest
import json

from config import Config
from database import Database
from scraper import ZhihuHotQuestionScraper

# 测试配置类
def test_config():
    """测试配置管理类"""
    # 创建临时配置文件
    test_config_path = "test_config.json"
    
    # 清理之前的测试文件
    if os.path.exists(test_config_path):
        os.remove(test_config_path)
    
    # 测试创建默认配置
    config = Config(test_config_path)
    assert config.get("scrape_count") == 20
    assert config.get("non_existent", "default") == "default"
    
    # 测试更新配置
    config.set("scrape_count", 10)
    assert config.get("scrape_count") == 10
    
    # 测试解析cookies
    test_cookies = "key1=value1; key2=value2"
    cookies_dict = config.parse_cookies(test_cookies)
    assert cookies_dict["key1"] == "value1"
    assert cookies_dict["key2"] == "value2"
    
    # 清理测试文件
    if os.path.exists(test_config_path):
        os.remove(test_config_path)

# 测试数据库类
def test_database():
    """测试数据库管理类"""
    # 创建测试数据库
    test_db_path = "test_database.db"
    
    # 清理之前的测试文件
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 初始化数据库
    db = Database(test_db_path)
    
    # 测试保存问题
    test_questions = [
        {
            "question_id": "12345",
            "title": "测试问题1",
            "hot_value": 100,
            "attention_increment": 10,
            "view_increment": 1000,
            "answer_increment": 5,
            "vote_increment": 20
        },
        {
            "question_id": "67890",
            "title": "测试问题2",
            "hot_value": 200,
            "attention_increment": 20,
            "view_increment": 2000,
            "answer_increment": 10,
            "vote_increment": 40
        }
    ]
    
    saved_count = db.save_questions(test_questions)
    assert saved_count == 2
    
    # 测试查询问题
    questions = db.get_questions(limit=10)
    assert len(questions) == 2
    
    # 测试查询总数
    count = db.get_question_count()
    assert count == 2
    
    # 测试去重逻辑
    duplicate_question = [
        {
            "question_id": "12345",  # 相同ID
            "title": "测试问题1更新版",
            "hot_value": 150,
            "attention_increment": 15
        }
    ]
    
    db.save_questions(duplicate_question)
    questions = db.get_questions(limit=10)
    # 数量应该仍然是2
    assert len(questions) == 2
    
    # 清理测试文件
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

# 测试爬虫类（需要有效的cookies）
@pytest.mark.asyncio
async def test_crawler():
    """测试爬虫功能（需要有效的cookies）"""
    
    # 创建测试配置
    test_config_path = "test_crawler_config.json"
    
    # 加载真实的cookies
    real_cookies = ""
    try:
        with open("config/config.json", "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
            real_cookies = loaded_config.get("cookies", "")
    except:
        # 如果无法加载，则跳过此测试
        pytest.skip("无法加载有效的cookies，跳过爬虫测试")
    
    if not real_cookies:
        pytest.skip("未提供有效的cookies，跳过爬虫测试")
    
    # 创建测试配置
    config = Config(test_config_path)
    config.set("cookies", real_cookies)
    config.set("scrape_count", 3)  # 只测试少量数据
    config.set("scroll_count", 1)  # 只滚动一次
    
    # 创建爬虫实例
    scraper = ZhihuHotQuestionScraper(config)
    
    try:
        # 执行爬取
        questions = await scraper.scrape()
        
        # 验证结果
        assert questions is not None
        # 可能获取的问题数量不等于请求的数量，但应该至少有一个
        assert len(questions) > 0
        
        # 验证问题结构
        first_question = questions[0]
        assert "question_id" in first_question
        assert "title" in first_question
        assert "hot_value" in first_question
        
    except Exception as e:
        pytest.fail(f"爬取过程中发生错误: {e}")
    
    finally:
        # 关闭爬虫
        await scraper.close()
        
        # 清理测试文件
        if os.path.exists(test_config_path):
            os.remove(test_config_path)

# 主函数，用于直接运行测试
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    print("测试配置类...")
    test_config()
    print("配置类测试通过 ✓")
    
    print("测试数据库类...")
    test_database()
    print("数据库类测试通过 ✓")
    
    print("测试爬虫类（需要有效的cookies）...")
    asyncio.run(test_crawler())
    print("爬虫类测试通过 ✓") 