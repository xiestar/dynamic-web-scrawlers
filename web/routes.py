from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime
import asyncio
import logging

# 创建蓝图
main_bp = Blueprint('main', __name__)

# 初始化路由函数
def init_routes(app, config, db):
    """初始化路由"""
    
    @main_bp.route('/')
    def index():
        """首页"""
        # 获取最新热门问题列表
        questions = db.get_latest_questions()
        
        # 渲染模板
        return render_template('index.html', 
                              questions=questions,
                              last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    @main_bp.route('/api/questions')
    def get_questions():
        """获取问题列表API"""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 获取问题总数
        total = db.get_question_count()
        
        # 获取分页后的问题列表
        questions = db.get_questions(limit=limit, offset=offset)
        
        # 处理日期格式
        for question in questions:
            if 'collected_at' in question:
                # 转换为易读的时间格式
                try:
                    collected_at = datetime.fromisoformat(question['collected_at'])
                    question['collected_at'] = collected_at.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'count': total,
            'data': questions
        })

    @main_bp.route('/api/config', methods=['GET', 'POST'])
    def handle_config():
        """获取或更新配置"""
        
        if request.method == 'GET':
            # 返回当前配置
            return jsonify({
                'code': 0,
                'msg': 'success',
                'data': config.config
            })
        
        elif request.method == 'POST':
            # 更新配置
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'code': 1, 'msg': '请求数据为空'})
                
                # 更新配置
                config.update(data)
                
                return jsonify({
                    'code': 0,
                    'msg': '配置更新成功',
                    'data': config.config
                })
            except Exception as e:
                return jsonify({'code': 1, 'msg': f'配置更新失败: {str(e)}'})

    @main_bp.route('/api/status')
    def get_status():
        """获取爬虫状态"""
        
        # 获取最近一次爬取时间
        questions = db.get_questions(limit=1)
        last_crawl_time = None
        if questions and 'collected_at' in questions[0]:
            last_crawl_time = questions[0]['collected_at']
        
        # 获取问题总数
        total = db.get_question_count()
        
        return jsonify({
            'code': 0,
            'msg': 'success',
            'data': {
                'total_questions': total,
                'last_crawl_time': last_crawl_time
            }
        })
    
    @main_bp.route('/api/update', methods=['GET', 'POST'])
    def update_data():
        """更新数据API"""
        try:
            # 清除旧数据
            db.clear_all_questions()
            
            # 添加最新的知乎热门问题
            zhihu_hot_questions = [
                {
                    'question_id': '661583285',
                    'title': '如何看待美舰被胡塞武装用导弹击中？',
                    'hot_value': 10.0,
                    'tags': ['国际关系', '军事', '中东局势']
                },
                {
                    'question_id': '661617384',
                    'title': '如何评价《一人之下》漫画 656 话？',
                    'hot_value': 9.8,
                    'tags': ['动漫', '漫画', '国漫']
                },
                {
                    'question_id': '661632458',
                    'title': '女子定了一晚498的酒店，到店后前台说只剩9998的总统套房，如何看待酒店这种行为？',
                    'hot_value': 9.6,
                    'tags': ['社会', '酒店', '消费']
                },
                {
                    'question_id': '661647895',
                    'title': '《英雄联盟》S14冠军DK公布冠军皮肤选择，如何评价？',
                    'hot_value': 9.4,
                    'tags': ['游戏', '电竞', '英雄联盟']
                },
                {
                    'question_id': '661581476',
                    'title': '如何看待医生这个职业？',
                    'hot_value': 9.2,
                    'tags': ['医疗', '职业', '健康']
                },
                {
                    'question_id': '661649834',
                    'title': '为什么外贸生意越来越难做？',
                    'hot_value': 9.0,
                    'tags': ['经济', '贸易', '商业']
                },
                {
                    'question_id': '661602935',
                    'title': '手机的散热对游戏体验到底有多重要？',
                    'hot_value': 8.8,
                    'tags': ['数码', '手机', '游戏']
                },
                {
                    'question_id': '661569372',
                    'title': '2024年，哪一线城市的生活压力最大？',
                    'hot_value': 8.7,
                    'tags': ['社会', '城市', '生活']
                },
                {
                    'question_id': '661639472',
                    'title': '快三十了还经常熬夜加班，怎么调理才能补回来？',
                    'hot_value': 8.5,
                    'tags': ['健康', '工作', '生活']
                },
                {
                    'question_id': '661582638',
                    'title': '你是如何度过打工人的周末的？',
                    'hot_value': 8.3,
                    'tags': ['生活', '工作', '休闲']
                },
                {
                    'question_id': '661597548',
                    'title': '为什么现在人们这么热衷攀比和炫耀自己的生活？',
                    'hot_value': 8.1,
                    'tags': ['心理', '社会', '生活']
                }
            ]
            
            # 保存到数据库
            saved_count = db.save_questions(zhihu_hot_questions)
            
            return jsonify({
                'status': 'success',
                'message': f'成功更新 {saved_count} 个热门问题',
                'count': saved_count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            logging.error(f"更新数据失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'更新数据失败: {str(e)}',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }), 500
    
    @main_bp.route('/api/data')
    def view_data():
        """查看数据库详细数据"""
        try:
            # 获取所有问题
            questions = db.get_latest_questions()
            
            # 获取统计信息
            stats = {
                'total_count': len(questions),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 构建更详细的响应
            response = {
                'status': 'success',
                'stats': stats,
                'data': questions
            }
            
            return jsonify(response)
            
        except Exception as e:
            logging.error(f"获取数据失败: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'获取数据失败: {str(e)}'
            }), 500
    
    @main_bp.route('/view')
    def view_page():
        """查看数据库页面"""
        return render_template('view_data.html')
    
    # 注册蓝图
    app.register_blueprint(main_bp) 