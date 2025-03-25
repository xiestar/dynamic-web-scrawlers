import json
import os
import logging

class Config:
    """配置管理类，负责加载和保存配置"""
    
    def __init__(self, config_path="config/config.json"):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config = self._default_config()
        self._ensure_config_path()
        self._load_config()
    
    def _ensure_config_path(self):
        """确保配置文件目录存在"""
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
    def _default_config(self):
        """返回默认配置"""
        return {
            "cookies": "",
            "scrape_count": 20,
            "scrape_interval": 3600, # 默认1小时采集一次
            "scroll_interval": 1000,  # 滚动间隔(毫秒)
            "scroll_count": 2,  # 滚动次数
            "database_path": "database/zhihu_hot_questions.db"
        }
    
    def _load_config(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 更新现有配置，保留默认值
                    self.config.update(loaded_config)
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")
        else:
            # 如果配置文件不存在，创建并保存默认配置
            self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项并保存"""
        self.config[key] = value
        self.save_config()
    
    def update(self, config_dict):
        """批量更新配置并保存"""
        self.config.update(config_dict)
        self.save_config()
    
    def parse_cookies(self, cookies_str):
        """解析cookies字符串为字典格式"""
        cookies_dict = {}
        if cookies_str:
            cookie_items = cookies_str.split('; ')
            for item in cookie_items:
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies_dict[key] = value
        return cookies_dict 