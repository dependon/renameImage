import os
import json
import locale

class LanguageManager:
    def __init__(self):
        self.current_language = None
        self.translations = {}
        self.locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        self.supported_languages = {
            'en': 'English',
            'zh': '中文',
            'ru': 'Русский',
            'ja': '日本語',
            'de': 'Deutsch',
            'pt': 'Português',
            'fr': 'Français'
        }
        
        # 初始化时自动检测系统语言
        system_lang = locale.getdefaultlocale()[0]
        self.default_language = 'en'  # 默认使用英语
        self.load_language(self.default_language)
    
    def load_language(self, lang_code):
        """加载指定的语言文件"""
        if lang_code not in self.supported_languages:
            lang_code = 'en'  # 默认使用英语
        
        try:
            file_path = os.path.join(self.locales_dir, f'{lang_code}.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = lang_code
            return True
        except Exception as e:
            print(f'Error loading language file: {e}')
            return False
    
    def get_text(self, key):
        """获取翻译文本"""
        return self.translations.get(key, key)
    
    def get_current_language(self):
        """获取当前语言代码"""
        return self.current_language
    
    def get_supported_languages(self):
        """获取支持的语言列表"""
        return self.supported_languages