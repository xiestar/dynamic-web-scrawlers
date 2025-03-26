"""
知乎热点问题自动采集脚本
"""
import asyncio
import logging
import time
import json
import sqlite3
import os
import schedule
from datetime import datetime
from playwright.async_api import async_playwright
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zhihu_crawler.log'),
        logging.StreamHandler()
    ]
)

# 数据库路径
DB_PATH = 'database/zhihu_hot_questions.db'

# 确保数据库目录存在
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

# 创建截图目录
SCREENSHOT_DIR = "screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# 用户提供的cookies字符串
COOKIES_STR = """_xsrf=2Vwy0xG40jul6rcNjp46j16d8JDN9h4E; __zse_ck=004_dvqa7RWZRV12Eq6GvyAOsCGjSRdsZZ2j98aFUk9vZ4t7dkQKJu4VhlXTBuxeWT/xscmWYU1hun4ySDpyxUmnVzKgNM3Ag6bqlLRjcCGyWX5gTQ1DkVu=v5TpTBKMzmWV-tVtsXc056E5/nO5Ehd9Yciw0f/gz0xFXHy0uPv43K8JYpEbOTsxOue8JHnXLWtl6MFC1Qy1B//NMU+qqFMkJ2h/B00nyIAlYNNo3+7BbntBdADHu5n+JhKakNXaB1xmq; _zap=6b7e3498-922a-47f5-8b73-644223550887; d_c0=CrCTJUK6JxqPTmiA9MpJ3gRlJOvzQO7KmRw=|1742122670; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1742122672,1742993179; HMACCOUNT=8FCE8C3610E0232E; captcha_session_v2=2|1:0|10:1742993179|18:captcha_session_v2|88:c0Vsa2RBUTVQdjBaWVBuWmhKM2FneHpBL2ZOL2lDWGlmLytYSVpnUWVvVHh3Rk96NmVCcm4rdnA1R2Y2dHhxOQ==|e9a8d8ea7ff28c563f0823df7e91f60a790c7b39421e4eb91dd5ee3b09500c41; SESSIONID=sbTEblgRUdMKXdmZOw6xypJeIE6YSmfJeMoi5X4pOd3; JOID=VFoRC0-0gnN8xhr3SkFjYi46psVSw-YrNaZylhTj4jg7knyeFq1_kBXAGP1K1ywp8WY-6w1dybC5JVASLv65lJA=; osd=V1kSAEq3gXB3wxn0SUpmYS05rcBRwOUgMKVxlR_m4Ts4mXmdFa50lRbDG_ZP1C8q-mM96A5WzLO6JlsXLf26n5U=; __snaker__id=iko5cOAICexzCESn; gdxidpyhxdE=N4RzD1uGzXsYoypNnEC%2B6%2FHG683tnYE9wm1BlbPKAt855SboCyc790lZaix2ka3Lgm2NNjfA0%5C86dfOMg0BDkLW6QrA2sl%2B%2Fe6v3Xt%2Fpk%5CZkf4%5CQPqErRy5ZzVAcM%2FtqHdPqEJPkE8QlpGe57WyUCwcddbDCqw3tV2y736O0EDzYh6ed%3A1742994079730; SUBMIT_0=9573159b-fed4-446e-b2d7-6e68fddb3bfc; z_c0=2|1:0|10:1742993207|4:z_c0|92:Mi4xRlV2OUFBQUFBQUFLc0pNbFFyb25HaVlBQUFCZ0FsVk5OVVhSYUFEbzJ6WHpqUDk2dkJVSDg3N0oxOXBrNkRldEZB|9fe95337b9f4017a5b03ff9f58d8c1e56881c6e5b46396166de878b8d7e2ec47; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1742993266; BEC=5ee33e0856ed13c879689106c041a08d"""

def parse_cookies(cookies_str):
    """解析cookies字符串为字典格式"""
    cookies = []
    for cookie in cookies_str.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            cookies.append({"name": name, "value": value, "domain": ".zhihu.com", "path": "/"})
    return cookies

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_table_exists():
    """确保数据表存在"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建问题表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id TEXT UNIQUE,
        title TEXT,
        hot_value REAL,
        attention_increment INTEGER DEFAULT 0,
        view_increment INTEGER DEFAULT 0,
        answer_increment INTEGER DEFAULT 0,
        vote_increment INTEGER DEFAULT 0,
        tags TEXT,
        collected_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("数据表结构已确认")

def save_questions(questions):
    """保存问题到数据库"""
    if not questions:
        logging.warning("没有问题数据可保存")
        return 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    saved_count = 0
    
    try:
        # 使用REPLACE INTO替代INSERT INTO，避免唯一约束冲突
        for question in questions:
            cursor.execute(
                "REPLACE INTO questions (question_id, title, hot_value, tags, collected_at) VALUES (?, ?, ?, ?, ?)",
                (
                    question['question_id'],
                    question['title'],
                    question['hot_value'],
                    json.dumps(question.get('tags', []), ensure_ascii=False),
                    datetime.now().isoformat()
                )
            )
            saved_count += 1
        
        conn.commit()
        logging.info(f"成功保存 {saved_count} 个问题到数据库")
    except Exception as e:
        logging.error(f"保存数据时出错: {str(e)}")
        conn.rollback()
    finally:
        conn.close()
    
    return saved_count

def get_random_user_agent():
    """获取随机用户代理"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    return random.choice(user_agents)

async def check_for_captcha(page):
    """检查页面是否有验证码"""
    captcha_selectors = [
        "text=系统监测到您的网络环境存在异常",
        "text=请点击下方验证按钮进行验证",
        ".Captcha-chinese",
        ".Captcha",
        "button:has-text('开始验证')"
    ]
    
    for selector in captcha_selectors:
        try:
            captcha_element = await page.query_selector(selector)
            if captcha_element:
                logging.warning(f"检测到验证码元素: {selector}")
                return True
        except Exception as e:
            continue
    
    return False

async def wait_for_human_verification(page):
    """等待人工处理验证码"""
    logging.info("等待人工处理验证码，请在浏览器中完成验证...")
    
    # 截图保存验证码页面
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "captcha.png"))
    
    # 等待人工处理，最多等待60秒
    max_wait_time = 60
    verification_completed = False
    
    for i in range(max_wait_time):
        # 检查验证码是否还存在
        captcha_exists = await check_for_captcha(page)
        if not captcha_exists:
            verification_completed = True
            logging.info("验证码已被处理，继续爬取")
            # 再等待一段时间让页面完全加载
            await asyncio.sleep(3)
            break
        
        # 等待1秒后再次检查
        await asyncio.sleep(1)
        if i % 5 == 0:  # 每5秒提示一次
            logging.info(f"等待验证码处理中... {i}/{max_wait_time}秒")
    
    if not verification_completed:
        logging.error("验证码处理超时")
        
    # 验证后重新截图
    await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "after_verification.png"))

async def extract_questions(page):
    """提取知乎热门问题"""
    questions = []
    logging.info("开始提取问题数据")
    
    # 首先尝试获取创作者中心热点问题的数据（通过API）
    try:
        logging.info("尝试从页面API获取问题数据")
        # 检查页面是否包含API数据
        has_api_data = await page.evaluate('''
            () => {
                const data = window.__INITIAL_STATE__ && 
                            window.__INITIAL_STATE__.creator && 
                            window.__INITIAL_STATE__.creator.hotQuestions;
                return !!data;
            }
        ''')
        
        if has_api_data:
            logging.info("找到API数据，尝试提取")
            questions_data = await page.evaluate('''
                () => {
                    const data = window.__INITIAL_STATE__.creator.hotQuestions;
                    return data || [];
                }
            ''')
            
            if questions_data and isinstance(questions_data, dict):
                logging.info(f"从API中提取到数据")
                
                # 从API数据中提取问题信息
                for key, value in questions_data.items():
                    if isinstance(value, dict) and 'title' in value and 'id' in value:
                        question_id = value.get('id')
                        title = value.get('title')
                        
                        # 提取热度值
                        hot_value = 0
                        if 'metricsArea' in value and isinstance(value['metricsArea'], dict):
                            metrics = value['metricsArea']
                            # 尝试获取热度值
                            if 'text' in metrics:
                                hot_text = metrics['text']
                                import re
                                hot_match = re.search(r'(\d+(\.\d+)?)', hot_text)
                                if hot_match:
                                    hot_value = float(hot_match.group(1))
                                    if '万' in hot_text:
                                        hot_value *= 10000
                        
                        # 提取标签
                        tags = []
                        if 'topics' in value and isinstance(value['topics'], list):
                            for topic in value['topics']:
                                if isinstance(topic, dict) and 'name' in topic:
                                    tags.append(topic['name'])
                        
                        questions.append({
                            'question_id': question_id,
                            'title': title,
                            'hot_value': hot_value,
                            'tags': tags
                        })
                
                if questions:
                    logging.info(f"成功从API提取 {len(questions)} 个问题")
                    return questions
    except Exception as e:
        logging.warning(f"尝试从API提取数据时出错: {str(e)}")
    
    # 如果API提取失败，回退到DOM提取
    logging.info("开始从DOM提取问题数据")
    
    # 多个可能的选择器，按优先级排序
    card_selectors = [
        ".CreatorHotQuestions-group .CreatorHotQuestions-item", # The most specific one for creator center
        ".CreatorHotQuestions-item",  # 创作者中心热点问题单项
        ".HotQuestions-item",  # 热门问题页面卡片
        ".HotQuestionsItem",  # 主页热门问题卡片
        ".Card.HotListCard-item",  # 热榜页面卡片
        ".QuestionItem",  # 问题项
        ".css-vurnku",  # 可能的卡片容器
        "div[role='listitem']",  # 列表项
        ".Card"  # 通用卡片
    ]
    
    # 尝试每个选择器
    cards = []
    for selector in card_selectors:
        try:
            logging.info(f"尝试使用选择器: {selector}")
            found_cards = await page.query_selector_all(selector)
            if found_cards and len(found_cards) > 0:
                logging.info(f"使用选择器 {selector} 找到 {len(found_cards)} 个卡片")
                cards = found_cards
                break
        except Exception as e:
            logging.warning(f"使用选择器 {selector} 时出错: {str(e)}")
    
    # 如果没有找到任何卡片，尝试分析页面HTML
    if not cards:
        logging.warning("未找到任何卡片，尝试分析页面HTML")
        try:
            # 获取页面HTML
            html = await page.content()
            
            # 查找包含问题ID的模式
            import re
            question_ids = re.findall(r'question/(\d+)', html)
            unique_ids = list(set(question_ids))
            
            logging.info(f"从HTML中找到 {len(unique_ids)} 个问题ID")
            
            # 如果找到问题ID，构建基本信息
            if unique_ids:
                for question_id in unique_ids[:30]:  # 限制最多处理30个问题
                    questions.append({
                        'question_id': question_id,
                        'title': f"问题ID: {question_id}",  # 无法获取标题，使用ID代替
                        'hot_value': 0,  # 无法获取热度，使用0代替
                        'tags': []  # 无法获取标签
                    })
                
                return questions
        except Exception as e:
            logging.error(f"尝试分析HTML时出错: {str(e)}")
    
    # 处理找到的卡片
    for i, card in enumerate(cards):
        try:
            question_data = {}
            
            # 提取问题ID
            try:
                # 尝试找到链接并提取ID
                link_element = await card.query_selector("a[href*='question']")
                if link_element:
                    href = await link_element.get_attribute("href")
                    if href:
                        import re
                        match = re.search(r'/question/(\d+)', href)
                        if match:
                            question_data['question_id'] = match.group(1)
            except Exception as e:
                logging.warning(f"提取问题ID时出错: {str(e)}")
            
            # 如果没有找到ID，跳过此卡片
            if 'question_id' not in question_data:
                continue
            
            # 提取标题
            try:
                # 尝试多个可能的标题选择器
                title_selectors = [
                    ".CreatorHotQuestions-title",  # 创作者中心热点问题标题
                    ".HotQuestionsItem-title",
                    ".QuestionItem-title",
                    ".ContentItem-title",
                    "h2",
                    "a[data-za-detail-view-element_name='Title']",
                    "a",
                    ".Card-title"
                ]
                
                for title_selector in title_selectors:
                    title_element = await card.query_selector(title_selector)
                    if title_element:
                        title = await title_element.inner_text()
                        if title:
                            question_data['title'] = title.strip()
                            break
            except Exception as e:
                logging.warning(f"提取标题时出错: {str(e)}")
            
            # 如果没有找到标题，使用默认值
            if 'title' not in question_data:
                question_data['title'] = f"未知标题-{question_data['question_id']}"
            
            # 提取热度值
            try:
                # 尝试多个可能的热度选择器
                hot_selectors = [
                    ".CreatorHotQuestions-metrics",  # 创作者中心热点问题热度
                    ".HotQuestionsItem-metrics",
                    ".HotQuestionsList-itemMeta",
                    ".NumberBoard-itemValue",
                    "span:has-text('热度')",
                    ".Card-footer"
                ]
                
                for hot_selector in hot_selectors:
                    hot_element = await card.query_selector(hot_selector)
                    if hot_element:
                        hot_text = await hot_element.inner_text()
                        if hot_text:
                            # 尝试提取数字部分
                            import re
                            hot_match = re.search(r'(\d+(\.\d+)?)', hot_text)
                            if hot_match:
                                hot_value = float(hot_match.group(1))
                                question_data['hot_value'] = hot_value
                                break
            except Exception as e:
                logging.warning(f"提取热度值时出错: {str(e)}")
            
            # 如果没有找到热度值，使用默认值
            if 'hot_value' not in question_data:
                question_data['hot_value'] = 0
            
            # 提取标签
            try:
                # 尝试找到标签元素
                tag_selectors = [
                    ".Tag",
                    ".TopicLink",
                    "a[data-za-detail-view-element_name='Topic']"
                ]
                
                tags = []
                for tag_selector in tag_selectors:
                    tag_elements = await card.query_selector_all(tag_selector)
                    if tag_elements:
                        for tag_element in tag_elements:
                            tag_text = await tag_element.inner_text()
                            if tag_text:
                                tags.append(tag_text.strip())
                        
                        if tags:
                            break
                
                question_data['tags'] = tags
            except Exception as e:
                logging.warning(f"提取标签时出错: {str(e)}")
            
            # 如果没有找到标签，使用空列表
            if 'tags' not in question_data:
                question_data['tags'] = []
            
            # 添加到结果列表
            questions.append(question_data)
            
        except Exception as e:
            logging.warning(f"处理第 {i+1} 个卡片时出错: {str(e)}")
    
    logging.info(f"成功提取 {len(questions)} 个问题")
    return questions

async def scroll_page(page):
    """滚动页面以加载更多内容"""
    logging.info("开始滚动页面...")
    
    try:
        # 获取页面高度
        initial_height = await page.evaluate('document.body.scrollHeight')
        logging.info(f"初始页面高度: {initial_height}")
        
        # 滚动次数
        scroll_count = 5
        
        for i in range(scroll_count):
            logging.info(f"执行第 {i+1}/{scroll_count} 次滚动")
            
            # 随机化滚动量
            scroll_amount = random.randint(500, 800)
            
            # 执行滚动
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            
            # 随机等待时间 (1-3秒)
            wait_time = 1 + 2 * random.random()
            logging.info(f"等待 {wait_time:.2f} 秒...")
            await asyncio.sleep(wait_time)
            
            # 检查是否触发了验证码
            has_captcha = await check_for_captcha(page)
            if has_captcha:
                logging.warning("滚动过程中检测到验证码")
                return
            
            # 获取新的高度
            new_height = await page.evaluate('document.body.scrollHeight')
            
            # 如果高度没有变化且已经滚动了几次，可能已经到底了
            if new_height == initial_height and i >= 3:
                logging.info("滚动后页面高度未变化，可能已经到达底部")
                break
            
            initial_height = new_height
        
        # 最后再返回顶部
        await page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)
        
    except Exception as e:
        logging.error(f"滚动页面时出错: {str(e)}")

async def crawl_zhihu_hot_questions():
    """爬取知乎热门问题"""
    logging.info("开始执行爬取任务")
    
    ensure_table_exists()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 非无头模式，方便验证码处理
        
        # 创建具有随机用户代理的上下文
        user_agent = get_random_user_agent()
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 720}
        )
        
        # 创建一个新页面
        page = await context.new_page()
        
        try:
            # 先访问一个简单页面，设置cookies
            await page.goto("https://www.zhihu.com")
            
            # 设置cookies
            cookies = parse_cookies(COOKIES_STR)
            await context.add_cookies(cookies)
            
            # 访问知乎创作者中心热点问题页面
            url = "https://www.zhihu.com/creator/hot-question/hot/0/hour"
            logging.info(f"正在访问: {url}")
            await page.goto(url)
            
            # 检查是否需要验证码
            if await check_for_captcha(page):
                verified = await wait_for_human_verification(page)
                if not verified:
                    logging.error("验证码处理失败，任务终止")
                    return
            
            # 滚动页面加载更多内容
            await scroll_page(page)
            
            # 提取问题数据
            questions = await extract_questions(page)
            
            # 保存数据到数据库
            save_questions(questions)
            
            # 保存截图
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = f"screenshots/zhihu_hot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            logging.info(f"页面截图已保存至 {screenshot_path}")
            
        except Exception as e:
            logging.error(f"爬取过程中出错: {e}")
        finally:
            await browser.close()
    
    logging.info("爬取任务执行完成")

def run_crawler():
    """运行爬虫任务"""
    logging.info("开始执行爬取任务")
    
    # 确保数据表存在
    ensure_table_exists()
    
    # 执行爬虫
    asyncio.run(crawl_zhihu_hot_questions())
    
    logging.info("爬取任务执行完成")

def schedule_crawler():
    """计划定期执行爬虫任务"""
    # 立即执行一次
    run_crawler()
    
    # 每小时执行一次
    schedule.every(1).hours.do(run_crawler)
    
    logging.info("已设置每小时自动爬取一次")
    
    # 持续运行调度器
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次是否有待执行的任务

if __name__ == "__main__":
    try:
        # 启动爬虫调度
        schedule_crawler()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc()) 