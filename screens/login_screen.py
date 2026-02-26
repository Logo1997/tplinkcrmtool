# -*- coding: utf-8 -*-
"""
登录屏幕
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from services import AuthService
from models import LoginResult


class LoginScreen(Screen):
    """登录屏幕"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()
        self._build_ui()
    
    def _build_ui(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        layout.add_widget(Label(
            text='TP-LINK CRM\n产品查询工具',
            font_size='28sp',
            size_hint=(1, 0.3),
            halign='center',
            valign='middle',
            color=(0.1, 0.56, 1, 1)
        ))
        
        layout.add_widget(Label(text='用户名', font_size='16sp', size_hint=(1, None), height=30, color=(0.4, 0.4, 0.4, 1)))
        self.username_input = TextInput(
            multiline=False,
            font_size='18sp',
            size_hint=(1, None),
            height=50,
            hint_text='请输入邮箱账号',
            background_color=(0.95, 0.97, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1)
        )
        layout.add_widget(self.username_input)
        
        layout.add_widget(Label(text='密码', font_size='16sp', size_hint=(1, None), height=30, color=(0.4, 0.4, 0.4, 1)))
        self.password_input = TextInput(
            password=True,
            multiline=False,
            font_size='18sp',
            size_hint=(1, None),
            height=50,
            hint_text='请输入密码',
            background_color=(0.95, 0.97, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1)
        )
        layout.add_widget(self.password_input)
        
        layout.add_widget(Label(size_hint=(1, 0.1)))
        
        self.login_btn = Button(
            text='登 录',
            font_size='20sp',
            size_hint=(1, None),
            height=55,
            background_color=(0.1, 0.56, 1, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.login_btn.bind(on_press=self._on_login)
        layout.add_widget(self.login_btn)
        
        self.status_label = Label(
            text='',
            font_size='14sp',
            size_hint=(1, None),
            height=40,
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size
    
    def _on_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username:
            self._show_popup('提示', '请输入用户名')
            return
        
        if not password:
            self._show_popup('提示', '请输入密码')
            return
        
        self.login_btn.disabled = True
        self.login_btn.text = '登录中...'
        self.status_label.text = '正在登录...'
        
        Clock.schedule_once(lambda dt: self._do_login(username, password), 0.1)
    
    def _do_login(self, username, password):
        result = self.auth_service.login(username, password)
        
        self.login_btn.disabled = False
        self.login_btn.text = '登 录'
        
        if result.success:
            self.status_label.text = f'登录成功: {result.user_name}'
            self.status_label.color = (0.2, 0.7, 0.3, 1)
            
            main_screen = self.manager.get_screen('main')
            main_screen.set_auth_service(self.auth_service, result.user_name, result.office_name)
            
            self.manager.current = 'main'
        else:
            self.status_label.text = f'登录失败: {result.message}'
            self.status_label.color = (0.9, 0.3, 0.3, 1)
            self._show_popup('登录失败', result.message)
    
    def _show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, font_size='16sp', color=(0.2, 0.2, 0.2, 1)),
            size_hint=(0.8, 0.3),
            background_color=(1, 1, 1, 1),
            separator_color=(0.1, 0.56, 1, 1)
        )
        popup.open()
    
    def load_saved_credentials(self):
        username, password = self.auth_service.get_saved_credentials()
        if username:
            self.username_input.text = username
        if password:
            self.password_input.text = password
