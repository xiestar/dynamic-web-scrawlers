# 知乎热点问题采集系统设计

## 项目概述
开发一个自动化系统，定期采集知乎创作者中心热点问题页面(https://www.zhihu.com/creator/hot-question/hot/0/hour)的数据，并存储到本地SQLite数据库中，同时提供简单的前端界面查看采集的数据。

## 系统需求
1. 使用playwright+cookies方式实现登录
2. 采集知乎热点问题前20个问题
3. 处理瀑布式加载的页面（向下滚动加载数据）
4. 数据去重保存到SQLite数据库
5. 提供简单的前端页面查看数据
6. 支持配置cookies、采集数量、采集间隔等参数

## 系统架构

### 1. 爬虫模块
- 使用playwright库进行网页自动化操作
- 使用cookies方式实现登录
- 实现页面滚动加载更多问题
- 提取问题标题、热力值、关注增量、浏览增量、回答增量等数据

### 2. 数据存储模块
- 使用SQLite数据库存储采集的数据
- 实现数据去重逻辑
- 数据表设计简洁实用

### 3. 配置模块
- 支持配置cookies信息
- 支持配置采集数量（默认20个）
- 支持配置采集间隔时间
- 配置信息保存在配置文件中

### 4. 前端界面
- 简单的Web界面展示采集的数据
- 支持基本的查询筛选功能
- 使用轻量级前端框架（如Flask+Bootstrap）

## 数据库设计

### 问题表(questions)
```sql
CREATE TABLE questions (
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
```

## 开发计划

### 阶段一：基础功能实现
1. 设置项目环境和依赖
2. 实现playwright自动登录功能
3. 实现页面滚动和数据采集
4. 实现SQLite数据存储

### 阶段二：配置和前端
1. 实现配置管理功能
2. 开发简单的前端界面
3. 实现基本的数据展示功能

### 阶段三：测试和优化
1. 测试爬虫稳定性
2. 优化数据采集效率
3. 修复问题和改进系统

## 技术栈
- 编程语言：Python
- 网页自动化：Playwright
- 数据库：SQLite
- 前端框架：Flask + Bootstrap
- 定时任务：内置scheduler或cron

## 注意事项
- 遵守知乎的robots.txt规则
- 控制采集频率，避免被封IP
- 定期更新cookies信息
- 保证数据完整性和准确性
- 关注系统稳定性和异常处理 