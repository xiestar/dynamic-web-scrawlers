from flask import Flask, render_template, jsonify, request, Blueprint
import os

def create_app(config, db):
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # 设置密钥
    app.secret_key = config.get('secret_key', os.urandom(24))
    
    # 配置
    app.config['DATABASE'] = db
    
    # 初始化路由
    from .routes import init_routes
    init_routes(app, config, db)
    
    return app 