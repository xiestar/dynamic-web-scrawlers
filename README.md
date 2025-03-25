# 知乎热点问题采集系统

这是一个自动化采集知乎创作者中心热点问题的系统，它能定期从知乎获取热点问题数据，并存储到本地SQLite数据库中，同时提供简单的Web界面查看数据。

## 功能特点

- 使用Playwright自动化浏览器实现登录和数据采集
- 支持瀑布式加载页面的处理（自动滚动加载更多内容）
- 数据去重保存到SQLite数据库
- 定时采集，可配置采集频率
- 简洁的Web界面查看已采集数据
- 可配置的爬虫参数（cookies、采集数量、采集间隔等）

## 安装步骤

1. 安装Python依赖：

```bash
pip install -r requirements.txt
```

2. 安装Playwright浏览器：

```bash
playwright install
```

3. 配置知乎Cookie：

从浏览器中获取知乎登录状态的Cookies，打开`config/config.json`配置文件，将Cookies字符串填入。

## 运行方式

启动应用：

```bash
python app.py
```

启动后，可以通过浏览器访问：`http://localhost:5000` 查看采集到的数据。

## 测试

运行测试：

```bash
# 使用pytest运行
pytest -v test_crawler.py

# 或者直接运行测试脚本
python test_crawler.py
```

## 目录结构

```
zhihu-crawler/
├── config/                 # 配置文件目录
│   └── config.json        # 配置文件
├── database/               # 数据库模块
│   └── __init__.py        # 数据库类
├── scraper/                # 爬虫模块
│   ├── __init__.py        # 爬虫模块初始化
│   └── crawler.py         # 爬虫实现
├── web/                    # Web界面模块
│   ├── __init__.py        # Web界面初始化
│   ├── routes.py          # Web路由
│   └── templates/         # 模板目录
│       └── index.html     # 首页模板
├── app.py                  # 主应用入口
├── config.py               # 配置管理类
├── requirements.txt        # 依赖列表
├── test_crawler.py         # 测试模块
└── README.md               # 项目说明
```

## 注意事项

- 爬虫需要有效的知乎登录Cookies才能正常工作
- 请合理设置采集频率，避免对知乎服务器造成过大压力
- 采集的数据仅用于个人学习和分析，请遵守知乎的使用条款

## 可能的问题排查

1. Cookies失效：知乎的Cookies有时效性，如果爬虫无法正常工作，可能需要更新Cookies
2. 页面结构变更：知乎可能会更新页面结构，如果爬虫无法正常提取数据，需要更新爬虫代码中的选择器
3. IP限制：频繁访问可能导致IP被限制，请合理设置采集频率 