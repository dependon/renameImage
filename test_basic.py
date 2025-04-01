import unittest
import os
import sys
from language_manager import LanguageManager

class TestBasicFunctionality(unittest.TestCase):
    def test_language_manager_initialization(self):
        """测试语言管理器初始化"""
        lm = LanguageManager()
        self.assertIsNotNone(lm.current_language)
        self.assertIsNotNone(lm.translations)
        self.assertTrue(os.path.exists(lm.locales_dir))
    
    def test_language_loading(self):
        """测试语言加载功能"""
        lm = LanguageManager()
        # 测试加载英语
        self.assertTrue(lm.load_language('en'))
        self.assertEqual(lm.current_language, 'en')
        # 测试加载中文
        self.assertTrue(lm.load_language('zh'))
        self.assertEqual(lm.current_language, 'zh')
        # 测试加载不存在的语言应该默认为英语
        self.assertTrue(lm.load_language('nonexistent'))
        self.assertEqual(lm.current_language, 'en')
    
    def test_text_retrieval(self):
        """测试文本获取功能"""
        lm = LanguageManager()
        lm.load_language('en')
        # 测试获取存在的键
        self.assertEqual(lm.get_text('title'), 'Batch Image Renaming Tool')
        # 测试获取不存在的键应该返回键本身
        self.assertEqual(lm.get_text('nonexistent_key'), 'nonexistent_key')
    
    def test_supported_languages(self):
        """测试支持的语言列表"""
        lm = LanguageManager()
        languages = lm.get_supported_languages()
        self.assertIsInstance(languages, dict)
        self.assertIn('en', languages)
        self.assertIn('zh', languages)
        self.assertEqual(languages['en'], 'English')
        self.assertEqual(languages['zh'], '中文')

if __name__ == '__main__':
    unittest.main()