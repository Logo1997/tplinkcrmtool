#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-LINK CRM 产品查询工具 - 移动版

主程序入口
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.lang import Builder

from screens import LoginScreen, MainScreen, DetailScreen, InventoryScreen
from services import CacheService
from config import init_android_assets

CHINESE_FONTS = [
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/simsun.ttc',
    '/system/fonts/DroidSansFallback.ttf',
    '/system/fonts/NotoSansCJK-Regular.ttc',
    '/system/fonts/NotoSansSC-Regular.otf',
]

def register_chinese_font():
    font_path = None
    for path in CHINESE_FONTS:
        if Path(path).exists():
            font_path = path
            break
    
    if font_path:
        LabelBase.register(name='ChineseFont', fn_regular=font_path)
        return 'ChineseFont'
    
    return 'Roboto'

KV_STYLE = '''
<Label>:
    font_name: 'ChineseFont'
    color: 0.2, 0.2, 0.2, 1

<Button>:
    font_name: 'ChineseFont'
    background_color: 0.1, 0.56, 1, 1
    background_normal: ''
    color: 1, 1, 1, 1

<TextInput>:
    font_name: 'ChineseFont'
    background_color: 1, 1, 1, 1
    foreground_color: 0.2, 0.2, 0.2, 1
    cursor_color: 0.1, 0.56, 1, 1

<ToggleButton>:
    font_name: 'ChineseFont'
    background_color: 0.9, 0.95, 1, 1
    background_normal: ''
    color: 0.2, 0.2, 0.2, 1

<ScrollView>:
    background_color: 1, 1, 1, 1

<BoxLayout>:
    background_color: 1, 1, 1, 1
'''

class TPLinkCRMApp(App):
    """TP-LINK CRM 应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_service = CacheService()
        self.font_name = register_chinese_font()
    
    def build(self):
        self.title = 'TP-LINK CRM 产品查询'
        
        init_android_assets()
        
        if platform != 'android':
            Window.size = (400, 700)
        
        Builder.load_string(KV_STYLE)
        
        sm = ScreenManager(transition=SlideTransition())
        
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DetailScreen(name='detail'))
        sm.add_widget(InventoryScreen(name='inventory'))
        
        self.cache_service.load()
        
        login_screen = sm.get_screen('login')
        login_screen.load_saved_credentials()
        
        return sm
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass


if __name__ == '__main__':
    TPLinkCRMApp().run()
