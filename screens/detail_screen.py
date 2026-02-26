# -*- coding: utf-8 -*-
"""
产品详情屏幕
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle

from services import ProductService, CacheService, CrawlerService
from models import ProductInfo, ProductFeatures


class InfoRow(BoxLayout):
    """信息行"""
    
    def __init__(self, label, value='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 35
        self.spacing = 10
        
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        label_widget = Label(
            text=label,
            font_size='14sp',
            size_hint_x=0.3,
            halign='left',
            valign='middle',
            color=(0.4, 0.4, 0.4, 1)
        )
        label_widget.bind(size=label_widget.setter('text_size'))
        self.add_widget(label_widget)
        
        self.value_label = Label(
            text=value,
            font_size='14sp',
            size_hint_x=0.55,
            halign='left',
            valign='middle',
            color=(0.1, 0.3, 0.5, 1)
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))
        self.add_widget(self.value_label)
        
        copy_btn = Button(
            text='复制',
            font_size='12sp',
            size_hint_x=0.15,
            background_color=(0.85, 0.9, 1, 1),
            background_normal='',
            color=(0.2, 0.2, 0.2, 1)
        )
        copy_btn.bind(on_press=lambda x: self._copy_value(value))
        self.add_widget(copy_btn)
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def set_value(self, value):
        self.value_label.text = str(value) if value else ''
    
    def _copy_value(self, value):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(str(value) if value else '')


class DetailScreen(Screen):
    """产品详情屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service = None
        self.cache_service = None
        self.crawler_service = CrawlerService()
        self._current_product = None
        self._current_features = None
        self._build_ui()
    
    def _build_ui(self):
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        
        back_btn = Button(
            text='← 返回',
            font_size='18sp',
            size_hint_x=0.2,
            background_color=(0.85, 0.9, 1, 1),
            background_normal='',
            color=(0.1, 0.3, 0.5, 1)
        )
        back_btn.bind(on_press=self._go_back)
        header.add_widget(back_btn)
        
        title = Label(
            text='产品详情',
            font_size='20sp',
            size_hint_x=0.8,
            halign='center',
            color=(0.1, 0.3, 0.5, 1)
        )
        header.add_widget(title)
        
        layout.add_widget(header)
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        basic_frame = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        basic_frame.bind(minimum_height=basic_frame.setter('height'))
        
        basic_grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        basic_grid.bind(minimum_height=basic_grid.setter('height'))
        
        self.model_row = InfoRow('产品型号:')
        self.name_row = InfoRow('产品名称:')
        self.brand_row = InfoRow('品牌:')
        self.series_row = InfoRow('系列:')
        self.lifecycle_row = InfoRow('生命周期:')
        
        basic_grid.add_widget(self.model_row)
        basic_grid.add_widget(self.brand_row)
        basic_grid.add_widget(self.name_row)
        basic_grid.add_widget(self.series_row)
        basic_grid.add_widget(Label(size_hint_y=None, height=35, color=(0.95, 0.97, 1, 1)))
        basic_grid.add_widget(self.lifecycle_row)
        
        basic_frame.add_widget(basic_grid)
        content.add_widget(basic_frame)
        
        price_frame = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        price_frame.bind(minimum_height=price_frame.setter('height'))
        
        price_title = Label(
            text='价格信息',
            font_size='16sp',
            size_hint_y=None,
            height=35,
            halign='left',
            color=(0.1, 0.56, 1, 1)
        )
        price_title.bind(size=price_title.setter('text_size'))
        price_frame.add_widget(price_title)
        
        self.price_row = InfoRow('价格:')
        self.discount_row = InfoRow('业务折扣:')
        self.high_discount_row = InfoRow('高折扣价:')
        self.low_discount_row = InfoRow('低折扣价:')
        
        price_frame.add_widget(self.price_row)
        price_frame.add_widget(self.discount_row)
        price_frame.add_widget(self.high_discount_row)
        price_frame.add_widget(self.low_discount_row)
        
        content.add_widget(price_frame)
        
        features_frame = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        features_frame.bind(minimum_height=features_frame.setter('height'))
        
        features_title = Label(
            text='产品参数',
            font_size='16sp',
            size_hint_y=None,
            height=35,
            halign='left',
            color=(0.1, 0.56, 1, 1)
        )
        features_title.bind(size=features_title.setter('text_size'))
        features_frame.add_widget(features_title)
        
        self.features_label = Label(
            text='',
            font_size='13sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.features_label.bind(texture_size=self.features_label.setter('size'))
        features_frame.add_widget(self.features_label)
        
        copy_features_btn = Button(
            text='复制全部参数',
            font_size='14sp',
            size_hint_y=None,
            height=40,
            background_color=(0.85, 0.9, 1, 1),
            background_normal='',
            color=(0.2, 0.2, 0.2, 1)
        )
        copy_features_btn.bind(on_press=self._copy_features)
        features_frame.add_widget(copy_features_btn)
        
        content.add_widget(features_frame)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.inventory_btn = Button(
            text='查询库存',
            font_size='18sp',
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.7, 0.4, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.inventory_btn.bind(on_press=self._show_inventory)
        layout.add_widget(self.inventory_btn)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def set_product(self, product, product_service, cache_service):
        self._current_product = product
        self.product_service = product_service
        self.cache_service = cache_service
        
        self.model_row.set_value(product.product_model)
        self.name_row.set_value(product.product_name[:30] if product.product_name else '')
        self.brand_row.set_value(product.brand)
        self.series_row.set_value(product.series)
        self.lifecycle_row.set_value(product.life_cycle_meaning)
        
        self.price_row.set_value(f"¥{product.price:,.0f}" if product.price else '')
        self.discount_row.set_value(product.business_discount or '')
        
        if product.high_discount_price and product.low_discount_price:
            self.high_discount_row.set_value(f"¥{product.high_discount_price:,}")
            self.low_discount_row.set_value(f"¥{product.low_discount_price:,}")
        else:
            self.high_discount_row.set_value('')
            self.low_discount_row.set_value('')
        
        self._load_features(product.product_model)
    
    def _load_features(self, model):
        features = self.cache_service.get(model)
        
        if features:
            self._current_features = features
            self._display_features(features)
        else:
            self.features_label.text = '正在从官网获取产品参数...'
            Clock.schedule_once(lambda dt: self._crawl_features(model), 0.1)
    
    def _crawl_features(self, model):
        features = self.crawler_service.crawl_product_by_model(model)
        
        if features:
            self._current_features = features
            self._display_features(features)
            self.cache_service.set(features)
        else:
            self.features_label.text = '⚠️ 官网无此产品参数'
            self._current_features = None
    
    def _display_features(self, features):
        if features and features.features:
            text = '\n'.join(f"• {f}" for f in features.features)
            self.features_label.text = text
        else:
            self.features_label.text = '暂无产品参数'
    
    def _copy_features(self, instance):
        if self._current_features and self._current_features.features:
            text = '\n'.join(self._current_features.features)
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            instance.text = '已复制'
            Clock.schedule_once(lambda dt: setattr(instance, 'text', '复制全部参数'), 1.5)
    
    def _go_back(self, instance):
        self.manager.current = 'main'
    
    def _show_inventory(self, instance):
        if self._current_product and self.product_service:
            self.inventory_btn.disabled = True
            self.inventory_btn.text = '查询中...'
            Clock.schedule_once(lambda dt: self._do_query_inventory(), 0.1)
    
    def _do_query_inventory(self):
        inventory_list = self.product_service.query_inventory(self._current_product.product_model)
        
        self.inventory_btn.disabled = False
        self.inventory_btn.text = '查询库存'
        
        inventory_screen = self.manager.get_screen('inventory')
        inventory_screen.set_product_with_data(self._current_product, inventory_list)
        self.manager.current = 'inventory'
