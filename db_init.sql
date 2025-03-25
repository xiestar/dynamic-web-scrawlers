-- 初始化数据库结构
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    hot_value REAL,
    attention_increment INTEGER,
    view_increment INTEGER,
    answer_increment INTEGER,
    vote_increment INTEGER,
    tags TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加测试数据
INSERT OR REPLACE INTO questions (question_id, title, hot_value, attention_increment, view_increment, answer_increment, vote_increment, tags, collected_at)
VALUES 
('15699023937', '「订婚强奸案」男方拒绝缓刑，上诉书称双方未发生实质性关系，怎样从法律角度解读？', 10.0, 95, 138000, 96, 4111, '#法律,#中国法律,#强奸案', CURRENT_TIMESTAMP),
('625762414', '为何很多人在谈论AI威胁时都在强调「智能」，而不是「自主」?', 8.5, 57, 93000, 85, 3520, '#人工智能,#AI,#技术', CURRENT_TIMESTAMP),
('557628284', '如何看待3月25日特斯拉官宣「中国业务总裁朱晓彤因个人原因离职」?', 9.2, 142, 210000, 63, 2835, '#特斯拉,#电动汽车,#商业', CURRENT_TIMESTAMP),
('621934578', '当下年轻人为什么开始流行「厨房手账」？记录做饭过程有什么意义？', 7.8, 124, 81000, 45, 1890, '#美食,#生活方式,#手账', CURRENT_TIMESTAMP),
('590283465', 'ChatGPT、Midjourney等AI工具是否正在威胁设计师的工作？', 8.0, 178, 135000, 92, 3248, '#AI,#设计,#职业发展', CURRENT_TIMESTAMP); 