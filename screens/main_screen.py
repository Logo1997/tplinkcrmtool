# -*- coding: utf-8 -*-
"""
主屏幕 - 产品搜索和列表
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle

from services import AuthService, ProductService, CacheService
from models import ProductInfo


class ProductItem(BoxLayout):
    """产品列表项"""
    
    def __init__(self, product, on_select, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = (10, 5)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        match_icon = '✓' if product.is_exact_match else '○'
        icon_color = (0.1, 0.56, 1, 1) if product.is_exact_match else (0.6, 0.6, 0.6, 1)
        
        icon_label = Label(
            text=match_icon,
            font_size='20sp',
            size_hint_x=0.1,
            color=icon_color
        )
        self.add_widget(icon_label)
        
        info_layout = BoxLayout(orientation='vertical', spacing=2)
        
        model_label = Label(
            text=product.product_model,
            font_size='16sp',
            size_hint_y=0.6,
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=(0.1, 0.3, 0.5, 1)
        )
        model_label.bind(size=model_label.setter('text_size'))
        info_layout.add_widget(model_label)
        
        name_text = product.product_name[:25] + '...' if len(product.product_name) > 25 else product.product_name
        name_label = Label(
            text=name_text,
            font_size='12sp',
            size_hint_y=0.4,
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1),
            text_size=(None, None)
        )
        name_label.bind(size=name_label.setter('text_size'))
        info_layout.add_widget(name_label)
        
        self.add_widget(info_layout)
        
        self.bind(on_touch_down=self._on_touch)
        self._on_select = on_select
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            if self._on_select:
                self._on_select(self.product)
            return True
        return False


class MainScreen(Screen):
    """主屏幕"""
    
    cache_info_text = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = None
        self.product_service = None
        self.cache_service = CacheService()
        self._products = []
        self._filtered_products = []
        self._current_product = None
        self._build_ui()
    
    def _build_ui(self):
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        
        self.title_label = Label(
            text='TP-LINK CRM 产品查询',
            font_size='20sp',
            halign='left',
            valign='middle',
            size_hint_x=0.7,
            color=(0.1, 0.3, 0.5, 1)
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        header.add_widget(self.title_label)
        
        self.cache_info_label = Label(
            text='',
            font_size='11sp',
            halign='right',
            valign='middle',
            color=(0.1, 0.56, 1, 1),
            size_hint_x=0.3
        )
        self.cache_info_label.bind(size=self.cache_info_label.setter('text_size'))
        header.add_widget(self.cache_info_label)
        
        layout.add_widget(header)
        
        search_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        
        self.search_input = TextInput(
            multiline=False,
            font_size='18sp',
            hint_text='输入产品型号搜索',
            size_hint_x=0.75,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1)
        )
        search_layout.add_widget(self.search_input)
        
        self.search_btn = Button(
            text='搜索',
            font_size='18sp',
            size_hint_x=0.25,
            background_color=(0.1, 0.56, 1, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.search_btn.bind(on_press=self._on_search)
        search_layout.add_widget(self.search_btn)
        
        layout.add_widget(search_layout)
        
        filter_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        
        self.hide_discontinued_btn = ToggleButton(
            text='不看停产设备',
            font_size='14sp',
            state='down',
            size_hint_x=0.5,
            background_color=(0.9, 0.95, 1, 1),
            background_normal='',
            color=(0.2, 0.2, 0.2, 1)
        )
        self.hide_discontinued_btn.bind(on_press=self._on_filter_changed)
        filter_layout.add_widget(self.hide_discontinued_btn)
        
        self.status_label = Label(
            text='请输入型号搜索',
            font_size='14sp',
            size_hint_x=0.5,
            color=(0.5, 0.5, 0.5, 1)
        )
        filter_layout.add_widget(self.status_label)
        
        layout.add_widget(filter_layout)
        
        self.list_container = BoxLayout(orientation='vertical')
        self.scroll_view = ScrollView()
        self.product_list = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None)
        self.product_list.bind(minimum_height=self.product_list.setter('height'))
        self.scroll_view.add_widget(self.product_list)
        self.list_container.add_widget(self.scroll_view)
        
        layout.add_widget(self.list_container)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def set_auth_service(self, auth_service, user_name, office_name):
        self.auth_service = auth_service
        self.product_service = ProductService(auth_service)
        
        self.title_label.text = f'{user_name} ({office_name})'
        
        self._refresh_cache_info()
    
    def _refresh_cache_info(self):
        cache_info = self.cache_service.get_cache_info()
        if cache_info['exists']:
            self.cache_info_label.text = f"缓存: {cache_info['total']}条"
        else:
            self.cache_info_label.text = "缓存: 未初始化"
    
    def _on_search(self, instance):
        model = self.search_input.text.strip()
        if not model:
            return
        
        self.search_btn.disabled = True
        self.search_btn.text = '搜索中...'
        self.status_label.text = '搜索中...'
        
        Clock.schedule_once(lambda dt: self._do_search(model), 0.1)
    
    def _do_search(self, model):
        products = self.product_service.search_products(model)
        self._products = products
        self._refresh_product_list()
        
        self.search_btn.disabled = False
        self.search_btn.text = '搜索'
    
    def _is_discontinued(self, product):
        return (product.life_cycle_meaning or '').strip() == '停产'
    
    def _on_filter_changed(self, instance):
        self._refresh_product_list()
    
    def _refresh_product_list(self):
        hide_discontinued = self.hide_discontinued_btn.state == 'down'
        
        if hide_discontinued:
            self._filtered_products = [p for p in self._products if not self._is_discontinued(p)]
        else:
            self._filtered_products = self._products
        
        self.product_list.clear_widgets()
        
        for product in self._filtered_products:
            item = ProductItem(product, self._on_product_select)
            self.product_list.add_widget(item)
        
        if self._filtered_products:
            total = len(self._products)
            filtered = len(self._filtered_products)
            if filtered < total:
                self.status_label.text = f'{filtered}个产品（过滤{total - filtered}个停产）'
            else:
                self.status_label.text = f'找到 {filtered} 个产品'
        else:
            self.status_label.text = '未找到匹配产品'
    
    def _on_product_select(self, product):
        self._current_product = product
        detail_screen = self.manager.get_screen('detail')
        detail_screen.set_product(product, self.product_service, self.cache_service)
        self.manager.current = 'detail'
