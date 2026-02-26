# -*- coding: utf-8 -*-
"""
CRM 认证服务
"""

import json
import time
import logging
import requests
from typing import Optional
from urllib.parse import urljoin

from config import CRM_CONFIG, QUERY_CONFIG, STORAGE_CONFIG
from models import LoginResult

logger = logging.getLogger(__name__)


class AuthService:
    """CRM认证服务"""
    
    def __init__(self):
        self.base_url = CRM_CONFIG['base_url']
        self.timeout = QUERY_CONFIG['timeout']
        self.max_retries = QUERY_CONFIG['max_retries']
        self.verify_ssl = QUERY_CONFIG.get('verify_ssl', True)
        self.session_file = STORAGE_CONFIG['session_file']
        
        self.session = requests.Session()
        self.is_logged_in = False
        self.user_info = None
        
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.base_url + '/crm/index.html',
            'X-Requested-With': 'XMLHttpRequest',
        })
    
    def login(self, username: str, password: str) -> LoginResult:
        """
        登录CRM系统
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            LoginResult对象
        """
        logger.info(f"正在登录CRM系统，用户名: {username}")
        
        login_url = urljoin(self.base_url, CRM_CONFIG['api_login'])
        
        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        
        payload = {
            'email': username,
            'password': password
        }
        
        try:
            response = self.session.post(
                login_url,
                data=payload,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            logger.info(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if 'sessionInfo' in result:
                    self.user_info = result.get('sessionInfo', {})
                    self.is_logged_in = True
                    
                    self.session.headers['Content-Type'] = 'application/json'
                    self._save_session(username, password)
                    
                    logger.info(f"登录成功！用户: {self.user_info.get('userName', 'unknown')}")
                    
                    return LoginResult(
                        success=True,
                        message='登录成功',
                        user_name=self.user_info.get('chineseName', ''),
                        office_name=self.user_info.get('officeName', '')
                    )
                else:
                    error_msg = result.get('message', '登录失败')
                    logger.error(f"登录失败: {error_msg}")
                    return LoginResult(
                        success=False,
                        message=error_msg
                    )
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"登录失败: {error_msg}")
                return LoginResult(
                    success=False,
                    message=error_msg
                )
                
        except requests.exceptions.ConnectionError:
            error_msg = "网络连接失败，请检查网络"
            logger.error(error_msg)
            return LoginResult(success=False, message=error_msg)
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请稍后重试"
            logger.error(error_msg)
            return LoginResult(success=False, message=error_msg)
        except Exception as e:
            error_msg = f"登录异常: {str(e)}"
            logger.error(error_msg)
            return LoginResult(success=False, message=error_msg)
    
    def _save_session(self, username: str, password: str):
        """保存会话信息"""
        try:
            session_data = {
                'cookies': dict(self.session.cookies),
                'username': username,
                'password': password,
                'user_info': self.user_info,
                'save_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
    
    def load_session(self) -> bool:
        """加载保存的会话"""
        if not self.session_file.exists():
            return False
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            cookies = session_data.get('cookies', {})
            self.session.cookies.update(cookies)
            self.user_info = session_data.get('user_info')
            
            test_url = urljoin(self.base_url, '/api/initHome')
            response = self.session.get(test_url, timeout=self.timeout, verify=self.verify_ssl)
            
            if response.status_code == 200:
                self.is_logged_in = True
                logger.info("会话验证成功")
                return True
            else:
                logger.info("会话已过期")
                return False
                
        except Exception as e:
            logger.warning(f"加载会话失败: {e}")
            return False
    
    def get_saved_credentials(self) -> tuple:
        """获取保存的凭证"""
        if not self.session_file.exists():
            return None, None
        
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            return session_data.get('username'), session_data.get('password')
        except Exception:
            return None, None
    
    def logout(self):
        """登出"""
        self.is_logged_in = False
        self.user_info = None
        self.session.close()
        if self.session_file.exists():
            self.session_file.unlink()
    
    def get(self, api_path: str, params: dict = None) -> Optional[dict]:
        """发起GET请求"""
        url = urljoin(self.base_url, api_path)
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout, 
                    verify=self.verify_ssl
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.warning("会话已过期")
                    return None
                else:
                    logger.warning(f"请求失败: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"请求异常 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
        
        return None
    
    def close(self):
        """关闭会话"""
        try:
            self.session.close()
        except Exception:
            pass
