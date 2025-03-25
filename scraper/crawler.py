import asyncio
import logging
import re
import os
import random
import json
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime

class ZhihuHotQuestionScraper:
    """知乎热点问题爬虫"""

    def __init__(self, config):
        """初始化爬虫"""
        self.config = config
        self.url = config.get('zhihu_hot_url', 'https://www.zhihu.com/creator/hot-question/hot/0/hour')
        self.cookies = []
        self.screenshot_dir = config.get('screenshot_dir', 'screenshots')
        
        # 确保截图目录存在
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        logging.info(f"初始化知乎热门问题爬虫，目标URL: {self.url}")
        
        self.scrape_count = config.get("scrape_count", 20)
        self.scroll_interval = config.get("scroll_interval", 1000)
        self.scroll_count = config.get("scroll_count", 2)
        self.browser = None
        self.page = None
        self.playwright = None
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ]
    
    def random_sleep(self, min_seconds=1, max_seconds=3):
        """随机等待一段时间，模拟人类行为"""
        sleep_time = random.uniform(min_seconds, max_seconds)
        logging.info(f"随机等待 {sleep_time:.2f} 秒")
        time.sleep(sleep_time)
    
    async def init_browser(self):
        """初始化浏览器"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)  # 使用有头模式便于调试
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            
            # 设置cookies
            cookies_list = []
            for key, value in self.cookies.items():
                cookies_list.append({
                    "name": key,
                    "value": value,
                    "domain": ".zhihu.com",
                    "path": "/"
                })
            
            if cookies_list:
                logging.info(f"设置 {len(cookies_list)} 个cookies")
                await self.context.add_cookies(cookies_list)
            else:
                logging.warning("没有可用的cookies，可能无法访问需要登录的页面")
            
            # 创建新页面
            self.page = await self.context.new_page()
            
            # 启用请求拦截以查看网络请求
            await self.page.route('**', self._log_request)
            
            # 导航到目标URL
            logging.info(f"导航到 {self.url}")
            await self.page.goto(self.url, wait_until="networkidle")
            
            # 保存页面截图
            await self.take_screenshot("initial_page.png")
            
            # 尝试检测登录状态
            await self._check_login_status()
            
            # 等待页面加载完成
            try:
                # 根据用户提供的HTML结构更新选择器
                selectors = [
                    '.css-vurnku',  # 根据用户提供的HTML
                    '.css-1fd22oq',
                    '.CreatorHomeLayout-mainColumn',
                    '.HotQuestions'
                ]
                
                for selector in selectors:
                    try:
                        logging.info(f"尝试等待选择器: {selector}")
                        await self.page.wait_for_selector(selector, timeout=5000)
                        logging.info(f"找到选择器: {selector}")
                        break
                    except Exception as e:
                        logging.warning(f"选择器 {selector} 未找到: {e}")
                
                logging.info("页面加载完成")
            except Exception as e:
                logging.error(f"页面加载失败: {e}")
                await self.take_screenshot("page_load_error.png")
                
                # 如果页面加载失败，尝试查找页面上的文本内容来判断页面状态
                page_content = await self.page.content()
                logging.info(f"页面内容片段: {page_content[:500]}...")
                
                # 尝试查找常见问题
                if "请登录" in page_content or "登录" in page_content:
                    logging.error("页面需要登录，cookies可能已过期")
                elif "验证" in page_content:
                    logging.error("页面需要人机验证，请手动处理")
                    await self.take_screenshot("captcha.png")
                    logging.info("已保存验证码截图到 captcha.png，请手动处理")
                
                raise
        except Exception as e:
            logging.error(f"初始化浏览器失败: {e}")
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            raise

    async def _log_request(self, route, request):
        """记录网络请求"""
        logging.debug(f"请求: {request.method} {request.url}")
        await route.continue_()
    
    async def _check_login_status(self):
        """检查登录状态"""
        try:
            # 检查是否有登录标识
            login_elements = await self.page.query_selector_all('[href^="/signin"]')
            if login_elements and len(login_elements) > 0:
                logging.warning("检测到登录链接，可能未登录状态")
                await self.take_screenshot("not_logged_in.png")
                
                # 尝试从页面中获取用户信息来确认登录状态
                user_avatar = await self.page.query_selector('.Avatar')
                if not user_avatar:
                    logging.error("无法找到用户头像，确认未登录状态")
            else:
                logging.info("检测到已登录状态")
        except Exception as e:
            logging.error(f"检查登录状态时出错: {e}")

    async def take_screenshot(self, filename):
        """保存页面截图，用于调试"""
        if self.page:
            full_path = os.path.join(self.screenshot_dir, filename)
            await self.page.screenshot(path=full_path)
            logging.info(f"截图已保存: {full_path}")
    
    async def scroll_page(self, page):
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
                
                # 每两次滚动后保存截图
                if i % 2 == 1:
                    await page.screenshot(path=os.path.join(self.screenshot_dir, f"scroll_{i+1}.png"))
                
                # 检查是否触发了验证码
                has_captcha = await self.check_for_captcha(page)
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
            
            # 保存最终滚动后的截图
            await page.screenshot(path=os.path.join(self.screenshot_dir, "scroll_complete.png"))
            logging.info("页面滚动完成")
            
        except Exception as e:
            logging.error(f"滚动页面时出错: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    async def extract_questions(self, page):
        """提取知乎热门问题"""
        questions = []
        logging.info("开始提取问题数据")
        
        # 多个可能的选择器，按优先级排序
        card_selectors = [
            ".HotQuestionsItem",  # 主页热门问题卡片
            ".HotQuestions-item",  # 热门问题页面卡片
            ".Card.HotListCard-item",  # 热榜页面卡片
            ".Card.AnswerCard",  # 答案卡片
            ".QuestionItem",  # 问题项
            ".css-vurnku",  # 可能的卡片容器
            "div[role='listitem']",  # 列表项
            ".Card"  # 通用卡片
        ]
        
        # 尝试每个选择器
        for selector in card_selectors:
            try:
                logging.info(f"尝试使用选择器: {selector}")
                cards = await page.query_selector_all(selector)
                logging.info(f"使用选择器 {selector} 找到 {len(cards)} 个卡片")
                
                if len(cards) > 0:
                    break
            except Exception as e:
                logging.warning(f"使用选择器 {selector} 时出错: {e}")
                continue
        
        # 如果没有找到任何卡片，尝试使用XPath
        if len(cards) == 0:
            logging.warning("未找到任何卡片，尝试使用XPath")
            try:
                # 尝试不同的XPath表达式
                xpath_expressions = [
                    "//div[contains(@class, 'Card')]",
                    "//div[contains(@class, 'Question')]",
                    "//div[contains(@class, 'List')]/div",
                    "//div[contains(@class, 'HotQuestions')]/div"
                ]
                
                for xpath in xpath_expressions:
                    cards = await page.query_selector_all(f"xpath={xpath}")
                    logging.info(f"使用XPath {xpath} 找到 {len(cards)} 个卡片")
                    if len(cards) > 0:
                        break
            except Exception as e:
                logging.warning(f"使用XPath时出错: {e}")
        
        # 如果仍然没有找到卡片，尝试分析页面HTML
        if len(cards) == 0:
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
                if len(unique_ids) > 0:
                    for question_id in unique_ids[:30]:  # 限制最多处理30个问题
                        questions.append({
                            'question_id': question_id,
                            'title': f"问题ID: {question_id}",  # 无法获取标题，使用ID代替
                            'hot_value': 0,  # 无法获取热度，使用0代替
                            'tags': []  # 无法获取标签
                        })
                    
                    return questions
            except Exception as e:
                logging.error(f"尝试分析HTML时出错: {e}")
        
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
                    logging.warning(f"提取问题ID时出错: {e}")
                
                # 如果没有找到ID，跳过此卡片
                if 'question_id' not in question_data:
                    continue
                
                # 提取标题
                try:
                    # 尝试多个可能的标题选择器
                    title_selectors = [
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
                    logging.warning(f"提取标题时出错: {e}")
                
                # 如果没有找到标题，使用默认值
                if 'title' not in question_data:
                    question_data['title'] = f"未知标题-{question_data['question_id']}"
                
                # 提取热度值
                try:
                    # 尝试多个可能的热度选择器
                    hot_selectors = [
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
                    logging.warning(f"提取热度值时出错: {e}")
                
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
                    logging.warning(f"提取标签时出错: {e}")
                
                # 如果没有找到标签，使用空列表
                if 'tags' not in question_data:
                    question_data['tags'] = []
                
                # 添加其他统计数据
                question_data['attention_increment'] = 0
                question_data['view_increment'] = 0
                question_data['answer_increment'] = 0
                question_data['vote_increment'] = 0
                
                # 添加到结果列表
                questions.append(question_data)
                
            except Exception as e:
                logging.warning(f"处理第 {i+1} 个卡片时出错: {e}")
        
        logging.info(f"成功提取 {len(questions)} 个问题")
        return questions
    
    def _parse_number(self, text):
        """将文本转换为数值"""
        if not text:
            return 0
            
        text = str(text).strip()
        
        # 处理"万"单位
        if "万" in text:
            return float(re.sub(r'[^\d.]', '', text)) * 10000
        
        # 处理"分"单位 (热力值)
        if "分" in text:
            return float(re.sub(r'[^\d.]', '', text))
        
        # 尝试提取数字
        match = re.search(r'[-+]?\d*\.?\d+', text)
        if match:
            return float(match.group())
        
        return 0
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape(self):
        """爬取知乎热门问题"""
        visible_mode = self.config.get('visible_mode', True)  # 默认为可视模式
        
        # 使用随机用户代理
        user_agent = self.get_random_user_agent()
        logging.info(f"使用用户代理: {user_agent}")
        logging.info(f"浏览器可视模式: {'开启' if visible_mode else '关闭'}")
        
        # 初始化 playwright
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=not visible_mode,  # 可视模式下设置为False
            )
            
            # 创建浏览器上下文
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
            )
            
            # 设置初始cookies
            if self.cookies:
                await context.add_cookies(self.cookies)
                logging.info(f"设置了 {len(self.cookies)} 个cookie")
            
            # 创建新页面
            page = await context.new_page()
            
            # 导航到目标URL
            logging.info(f"正在访问: {self.url}")
            await page.goto(self.url)
            
            # 保存初始页面截图
            await page.screenshot(path=os.path.join(self.screenshot_dir, "initial_page.png"))
            
            # 检查页面的基本元素
            await self.check_page_elements(page)
            
            # 检查是否有验证码
            has_captcha = await self.check_for_captcha(page)
            if has_captcha:
                # 保存验证码页面截图
                await page.screenshot(path=os.path.join(self.screenshot_dir, "captcha_detected.png"))
                
                if visible_mode:
                    # 有头模式下等待人工验证
                    await self.wait_for_human_verification(page)
                else:
                    # 无头模式下无法处理验证码
                    logging.error("无头模式下检测到验证码，无法处理。请使用可视模式运行")
                    return []
            
            # 尝试等待页面加载
            try:
                # 尝试等待多个可能的选择器
                selectors = [".css-vurnku", ".css-1fd22oq", ".CreatorHomeLayout-mainColumn", ".HotQuestions"]
                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        logging.info(f"成功找到选择器: {selector}")
                        break
                    except Exception as e:
                        logging.warning(f"等待选择器 {selector} 超时: {e}")
            except Exception as e:
                logging.warning(f"等待页面加载超时: {e}")
            
            # 等待页面完全加载
            await page.wait_for_load_state("networkidle")
            
            # 页面滚动
            await self.scroll_page(page)
            
            # 提取问题数据
            questions = await self.extract_questions(page)
            
            # 如果没有找到问题数据，检查是否有验证码
            if not questions:
                logging.warning("未找到问题数据，检查是否有验证码")
                # 保存未找到问题数据的页面截图
                await page.screenshot(path=os.path.join(self.screenshot_dir, "no_questions_found.png"))
                
                has_captcha = await self.check_for_captcha(page)
                if has_captcha:
                    if visible_mode:
                        # 有头模式下等待人工验证
                        await self.wait_for_human_verification(page)
                        # 再次尝试提取问题
                        questions = await self.extract_questions(page)
                    else:
                        logging.error("无头模式下检测到验证码，无法处理")
            
            if questions:
                logging.info(f"成功爬取到 {len(questions)} 个问题")
                # 保存成功页面截图
                await page.screenshot(path=os.path.join(self.screenshot_dir, "success.png"))
            else:
                logging.warning("未爬取到任何问题")
                # 保存失败页面截图
                await page.screenshot(path=os.path.join(self.screenshot_dir, "failure.png"))
            
            # 更新cookies
            cookies = await context.cookies()
            self.cookies = cookies
            logging.info(f"更新了 {len(cookies)} 个cookies")
            
            # 关闭浏览器
            await browser.close()
            await playwright.stop()
            
            return questions
            
        except Exception as e:
            logging.error(f"爬取过程中发生错误: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return []

    async def check_for_captcha(self, page):
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
    
    async def wait_for_human_verification(self, page):
        """等待人工处理验证码"""
        logging.info("等待人工处理验证码，请在浏览器中完成验证...")
        
        # 截图保存验证码页面
        await page.screenshot(path=os.path.join(self.screenshot_dir, "captcha.png"))
        
        # 等待人工处理，最多等待60秒
        max_wait_time = 60
        verification_completed = False
        
        for i in range(max_wait_time):
            # 检查验证码是否还存在
            captcha_exists = await self.check_for_captcha(page)
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
        await page.screenshot(path=os.path.join(self.screenshot_dir, "after_verification.png"))
        
    async def check_page_elements(self, page):
        """检查页面上的基本元素，用于调试"""
        try:
            # 获取页面内容
            body_text = await page.inner_text("body")
            logging.info(f"Body文本片段: {body_text[:200]}")
            
            # 检查是否有验证码相关内容
            if "验证" in body_text or "captcha" in body_text.lower():
                logging.warning("页面内容中包含验证相关文本")
            
            # 检查基本元素
            basic_selectors = ["h1", "a", "div", "span", "img"]
            for selector in basic_selectors:
                elements = await page.query_selector_all(selector)
                logging.info(f"找到 {len(elements)} 个 {selector} 元素")
        
        except Exception as e:
            logging.error(f"检查页面元素时出错: {e}") 

    def get_random_user_agent(self):
        """获取随机用户代理"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
        ]
        return random.choice(user_agents) 