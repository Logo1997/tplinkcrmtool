# -*- coding: utf-8 -*-
"""
库存屏幕
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from services import ProductService
from models import ProductInfo, InventoryInfo


class InventoryItem(GridLayout):
    """库存列表项"""
    
    def __init__(self, inventory, **kwargs):
        super().__init__(**kwargs)
        self.cols = 4
        self.size_hint_y = None
        self.height = 45
        self.spacing = 5
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.add_widget(Label(
            text=inventory.sub_inventory[:15] if inventory.sub_inventory else '',
            font_size='13sp',
            halign='center',
            color=(0.2, 0.2, 0.2, 1)
        ))
        
        qty_text = str(inventory.quantity)
        qty_color = (0.2, 0.7, 0.3, 1) if inventory.quantity > 0 else (0.5, 0.5, 0.5, 1)
        self.add_widget(Label(
            text=qty_text,
            font_size='13sp',
            color=qty_color,
            halign='center'
        ))
        
        self.add_widget(Label(
            text=str(inventory.in_transit or 0),
            font_size='13sp',
            halign='center',
            color=(0.2, 0.2, 0.2, 1)
        ))
        
        self.add_widget(Label(
            text=inventory.price_info[:10] if inventory.price_info else '',
            font_size='13sp',
            halign='center',
            color=(0.2, 0.2, 0.2, 1)
        ))
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size


class InventoryScreen(Screen):
    """库存屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service = None
        self._current_product = None
        self._inventory_list = []
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
        
        self.title_label = Label(
            text='库存信息',
            font_size='20sp',
            size_hint_x=0.8,
            halign='center',
            color=(0.1, 0.3, 0.5, 1)
        )
        header.add_widget(self.title_label)
        
        layout.add_widget(header)
        
        table_header = GridLayout(cols=4, size_hint=(1, None), height=40, spacing=5)
        table_header.add_widget(Label(text='仓库', font_size='14sp', bold=True, color=(0.1, 0.56, 1, 1)))
        table_header.add_widget(Label(text='库存', font_size='14sp', bold=True, color=(0.1, 0.56, 1, 1)))
        table_header.add_widget(Label(text='在途', font_size='14sp', bold=True, color=(0.1, 0.56, 1, 1)))
        table_header.add_widget(Label(text='价格', font_size='14sp', bold=True, color=(0.1, 0.56, 1, 1)))
        layout.add_widget(table_header)
        
        self.scroll_view = ScrollView()
        self.inventory_list = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None)
        self.inventory_list.bind(minimum_height=self.inventory_list.setter('height'))
        self.scroll_view.add_widget(self.inventory_list)
        layout.add_widget(self.scroll_view)
        
        summary_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        
        self.total_label = Label(
            text='总库存: 0',
            font_size='16sp',
            color=(0.1, 0.56, 1, 1),
            size_hint_x=0.5
        )
        summary_layout.add_widget(self.total_label)
        
        self.status_label = Label(
            text='',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.5
        )
        summary_layout.add_widget(self.status_label)
        
        layout.add_widget(summary_layout)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def set_product(self, product, product_service):
        self._current_product = product
        self.product_service = product_service
        
        self.title_label.text = f'{product.product_model} 库存'
        self._query_inventory(product.product_model)
    
    def set_product_with_data(self, product, inventory_list):
        self._current_product = product
        self._inventory_list = inventory_list
        
        self.title_label.text = f'{product.product_model} 库存'
        self._display_inventory(inventory_list)
    
    def _query_inventory(self, model):
        self.inventory_list.clear_widgets()
        self.status_label.text = '查询中...'
        
        Clock.schedule_once(lambda dt: self._do_query(model))
    
    def _do_query(self, model):
        inventory_list = self.product_service.query_inventory(model)
        self._inventory_list = inventory_list
        self._display_inventory(inventory_list)
    
    def _display_inventory(self, inventory_list):
        self.inventory_list.clear_widgets()
        
        total_quantity = 0
        
        for inv in inventory_list:
            item = InventoryItem(inv)
            self.inventory_list.add_widget(item)
            total_quantity += inv.quantity
        
        self.total_label.text = f'总库存: {total_quantity}'
        
        if inventory_list:
            self.status_label.text = f'共 {len(inventory_list)} 条记录'
        else:
            self.status_label.text = '暂无库存记录'
    
    def _go_back(self, instance):
        self.manager.current = 'detail'
