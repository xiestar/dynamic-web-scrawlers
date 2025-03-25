"""
添加测试数据到数据库，用于测试前端显示
"""
import logging
from datetime import datetime
from database import Database

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 创建测试数据
test_questions = [
    {
        "question_id": "15699023937",
        "title": "「订婚强奸案」男方拒绝缓刑，上诉书称双方未发生实质性关系，怎样从法律角度解读？",
        "hot_value": 10.0,
        "attention_increment": 95,
        "view_increment": 138000,
        "answer_increment": 96,
        "vote_increment": 4111,
        "tags": "#法律,#中国法律,#强奸案"
    },
    {
        "question_id": "625762414",
        "title": "为何很多人在谈论AI威胁时都在强调「智能」，而不是「自主」?",
        "hot_value": 8.5,
        "attention_increment": 57,
        "view_increment": 93000,
        "answer_increment": 85,
        "vote_increment": 3520,
        "tags": "#人工智能,#AI,#技术"
    },
    {
        "question_id": "557628284",
        "title": "如何看待3月25日特斯拉官宣「中国业务总裁朱晓彤因个人原因离职」?",
        "hot_value": 9.2,
        "attention_increment": 142,
        "view_increment": 210000,
        "answer_increment": 63,
        "vote_increment": 2835,
        "tags": "#特斯拉,#电动汽车,#商业"
    },
    {
        "question_id": "621934578",
        "title": "当下年轻人为什么开始流行「厨房手账」？记录做饭过程有什么意义？",
        "hot_value": 7.8,
        "attention_increment": 124,
        "view_increment": 81000,
        "answer_increment": 45,
        "vote_increment": 1890,
        "tags": "#美食,#生活方式,#手账"
    },
    {
        "question_id": "590283465",
        "title": "ChatGPT、Midjourney等AI工具是否正在威胁设计师的工作？",
        "hot_value": 8.0,
        "attention_increment": 178,
        "view_increment": 135000,
        "answer_increment": 92,
        "vote_increment": 3248,
        "tags": "#AI,#设计,#职业发展"
    },
    {
        "question_id": "586214753",
        "title": "2025年考研报名人数或将突破500万，竞争越来越激烈，考研还值得吗？",
        "hot_value": 8.7,
        "attention_increment": 389,
        "view_increment": 320000,
        "answer_increment": 152,
        "vote_increment": 5472,
        "tags": "#考研,#教育,#职业规划"
    },
    {
        "question_id": "548792168",
        "title": "如何看待某互联网公司HR称「本科双非，研究生成绩一般，没有突出的背景，但要价25k，太贵了」?",
        "hot_value": 9.5,
        "attention_increment": 432,
        "view_increment": 480000,
        "answer_increment": 189,
        "vote_increment": 7850,
        "tags": "#职场,#互联网,#求职"
    },
    {
        "question_id": "590873624",
        "title": "你最近悟出了什么人生哲理？",
        "hot_value": 7.6,
        "attention_increment": 87,
        "view_increment": 79000,
        "answer_increment": 148,
        "vote_increment": 3250,
        "tags": "#哲学,#思考,#人生感悟"
    },
    {
        "question_id": "342356872",
        "title": "每天坚持运动一小时，半年后身体会有哪些变化？",
        "hot_value": 8.2,
        "attention_increment": 215,
        "view_increment": 187000,
        "answer_increment": 78,
        "vote_increment": 4120,
        "tags": "#健身,#运动,#健康"
    },
    {
        "question_id": "634891257",
        "title": "如何看待2025年3月25日A股市场表现？后市如何走向？",
        "hot_value": 7.9,
        "attention_increment": 165,
        "view_increment": 142000,
        "answer_increment": 37,
        "vote_increment": 1520,
        "tags": "#投资,#股市,#财经"
    },
    {
        "question_id": "589761435",
        "title": "长期独处会让人变得更聪明还是更愚蠢？",
        "hot_value": 8.4,
        "attention_increment": 203,
        "view_increment": 198000,
        "answer_increment": 112,
        "vote_increment": 4870,
        "tags": "#心理学,#独处,#思考"
    },
    {
        "question_id": "412568723",
        "title": "为什么越来越多的年轻人选择不婚不育？这种生活方式可持续吗？",
        "hot_value": 9.1,
        "attention_increment": 321,
        "view_increment": 347000,
        "answer_increment": 231,
        "vote_increment": 8420,
        "tags": "#社会,#婚姻,#生活方式"
    },
    {
        "question_id": "597123456",
        "title": "工作10年后，你觉得最重要的能力是什么？",
        "hot_value": 8.9,
        "attention_increment": 276,
        "view_increment": 289000,
        "answer_increment": 186,
        "vote_increment": 6350,
        "tags": "#职场,#能力,#职业发展"
    },
    {
        "question_id": "623781945",
        "title": "如何看待游戏《黑神话：悟空》最新公布的实机演示？",
        "hot_value": 9.3,
        "attention_increment": 487,
        "view_increment": 523000,
        "answer_increment": 138,
        "vote_increment": 7890,
        "tags": "#游戏,#黑神话悟空,#国产游戏"
    },
    {
        "question_id": "587643219",
        "title": "你每天坚持写日记了吗？写日记有什么好处？",
        "hot_value": 7.5,
        "attention_increment": 92,
        "view_increment": 75000,
        "answer_increment": 83,
        "vote_increment": 2780,
        "tags": "#写作,#日记,#生活习惯"
    },
    {
        "question_id": "612378945",
        "title": "如何评价近期流行的「全家桶基金」？普通人该如何进行基金定投？",
        "hot_value": 8.3,
        "attention_increment": 198,
        "view_increment": 176000,
        "answer_increment": 42,
        "vote_increment": 2950,
        "tags": "#基金,#投资,#理财"
    },
    {
        "question_id": "578923416",
        "title": "为什么很多人喜欢逛超市但不喜欢逛菜市场？",
        "hot_value": 7.7,
        "attention_increment": 127,
        "view_increment": 94000,
        "answer_increment": 115,
        "vote_increment": 3480,
        "tags": "#消费,#购物,#生活方式"
    },
    {
        "question_id": "609871234",
        "title": "现在的年轻人为什么都不愿意拼命了？",
        "hot_value": 9.0,
        "attention_increment": 398,
        "view_increment": 412000,
        "answer_increment": 245,
        "vote_increment": 9520,
        "tags": "#社会,#年轻人,#工作"
    },
    {
        "question_id": "592837461",
        "title": "你在生活中有哪些省钱的小妙招？",
        "hot_value": 8.1,
        "attention_increment": 183,
        "view_increment": 162000,
        "answer_increment": 197,
        "vote_increment": 5270,
        "tags": "#理财,#省钱,#生活"
    },
    {
        "question_id": "637218945",
        "title": "长时间看手机对视力的影响有多大？如何保护眼睛？",
        "hot_value": 8.6,
        "attention_increment": 219,
        "view_increment": 203000,
        "answer_increment": 74,
        "vote_increment": 3980,
        "tags": "#健康,#眼睛,#手机"
    }
]

def add_test_data():
    """添加测试数据到数据库"""
    db = None
    try:
        # 初始化数据库
        db = Database()
        
        # 保存测试数据
        saved_count = db.save_questions(test_questions)
        
        logging.info(f"成功添加 {saved_count} 个测试问题到数据库")
        
        # 查询验证
        questions = db.get_questions(limit=5)
        logging.info(f"数据库中最新的问题:")
        for i, q in enumerate(questions):
            logging.info(f"{i+1}. {q['title']} (热力值: {q['hot_value']})")
        
        total_count = db.get_question_count()
        logging.info(f"数据库总问题数: {total_count}")
        
        return saved_count
    except Exception as e:
        logging.error(f"添加测试数据失败: {e}")
        return 0
    finally:
        # 确保关闭数据库连接
        if db:
            db._close_connection()

if __name__ == "__main__":
    add_test_data() 