# -*- coding: utf-8 -*-
"""
产品参数爬虫服务
"""

import re
import time
import logging
import requests
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import WEBSITE_CONFIG, CRAWLER_CONFIG
from models import ProductFeatures

logger = logging.getLogger(__name__)


class CrawlerService:
    """产品参数爬虫服务"""
    
    FOCAL_LENGTH_SUFFIXES = ['2.8', '4', '6', '8', '12', '16', '2.8mm', '4mm', '6mm', '8mm', '12mm', '16mm']
    
    def __init__(self):
        self.base_url = WEBSITE_CONFIG['base_url']
        self.product_url_template = WEBSITE_CONFIG['product_url_template']
        self.search_url = WEBSITE_CONFIG['search_url']
        self.max_product_id = WEBSITE_CONFIG['max_product_id']
        
        self.timeout = CRAWLER_CONFIG['timeout']
        self.request_delay = CRAWLER_CONFIG['request_delay']
    
    def _create_session(self) -> requests.Session:
        """创建新的会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def _normalize_model_for_search(self, model: str) -> str:
        """
        规范化型号用于搜索
        
        对于摄像机型号（如 TL-IPC445GP-2.8），去除焦距后缀
        TL-IPC445GP-2.8 -> TL-IPC445GP
        TL-IPC445GP-4 -> TL-IPC445GP
        TL-IPCABC-DN -> TL-IPCABC-D (如果D不为空) 或 TL-IPCABC (如果D为空)
        """
        if not model:
            return model
        
        model_upper = model.upper().strip()
        
        for suffix in self.FOCAL_LENGTH_SUFFIXES:
            suffix_upper = suffix.upper()
            if model_upper.endswith('-' + suffix_upper):
                model_upper = model_upper[:-len(suffix_upper)-1]
                break
            elif model_upper.endswith(suffix_upper):
                model_upper = model_upper[:-len(suffix_upper)]
                if model_upper.endswith('-'):
                    model_upper = model_upper[:-1]
                break
        
        return model_upper
    
    def _calculate_match_score(self, crm_model: str, result_model: str) -> int:
        """
        计算型号匹配得分
        
        Args:
            crm_model: CRM中的产品型号
            result_model: 搜索结果中的产品型号
            
        Returns:
            匹配得分，越高越匹配
        """
        if not crm_model or not result_model:
            return 0
        
        crm_upper = crm_model.upper().strip()
        result_upper = result_model.upper().strip()
        
        if crm_upper == result_upper:
            return 100
        
        crm_normalized = self._normalize_model_for_search(crm_upper)
        result_normalized = self._normalize_model_for_search(result_upper)
        
        if crm_normalized == result_normalized:
            return 90
        
        if crm_normalized == result_upper:
            return 85
        
        if result_normalized.startswith(crm_normalized):
            return 80
        
        if crm_normalized.startswith(result_normalized):
            return 75
        
        crm_base = re.sub(r'[\-_].*$', '', crm_normalized)
        result_base = re.sub(r'[\-_].*$', '', result_normalized)
        
        if crm_base and result_base and crm_base == result_base:
            return 70
        
        if crm_normalized in result_normalized:
            return 60
        
        if result_normalized in crm_normalized:
            return 50
        
        return 0
    
    def crawl_product_by_model(self, model: str) -> Optional[ProductFeatures]:
        """
        根据型号爬取产品参数
        
        Args:
            model: 产品型号
            
        Returns:
            ProductFeatures对象，未找到或型号不匹配返回None
        """
        logger.info(f"爬取产品参数: {model}")
        
        session = self._create_session()
        try:
            product_url, product_name, matched_model = self._search_product(session, model)
            
            if not product_url:
                logger.warning(f"未找到产品: {model}")
                return None
            
            features = self._get_product_features(session, product_url, model)
            
            if not features:
                return None
            
            if not self._verify_model_match(model, features.product_model):
                logger.warning(f"型号不匹配: CRM型号={model}, 官网型号={features.product_model}")
                return None
            
            features.product_name = product_name or features.product_name
            
            return features
        finally:
            session.close()
    
    def _verify_model_match(self, crm_model: str, website_model: str) -> bool:
        """
        验证CRM型号与官网型号是否匹配
        
        Args:
            crm_model: CRM中的产品型号
            website_model: 官网获取的产品型号
            
        Returns:
            是否匹配
        """
        if not crm_model or not website_model:
            return False
        
        score = self._calculate_match_score(crm_model, website_model)
        return score >= 70
    
    def _search_product(self, session: requests.Session, model: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        搜索产品页面，从搜索结果中选择最匹配的产品
        
        Args:
            session: HTTP会话
            model: 产品型号
            
        Returns:
            (产品URL, 产品名称, 匹配的型号)
        """
        search_model = self._normalize_model_for_search(model)
        logger.info(f"搜索型号: {model} -> 规范化: {search_model}")
        
        params = {'keywords': model}
        
        try:
            response = session.get(
                self.search_url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            time.sleep(self.request_delay)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            result_items = soup.select('div.resultDetail')
            
            for item in result_items:
                search_img = item.select_one('div.searchImg a')
                search_model_elem = item.select_one('p.searchModel')
                search_name = item.select_one('h3.searchName a')
                
                if search_img and search_model_elem:
                    href = search_img.get('href', '')
                    if href:
                        full_url = self.base_url + href if href.startswith('/') else href
                        result_model = search_model_elem.get_text(strip=True)
                        product_name = ""
                        
                        if search_name:
                            product_name = search_name.get_text(strip=True)
                        
                        score = self._calculate_match_score(model, result_model)
                        
                        results.append({
                            'url': full_url,
                            'model': result_model,
                            'name': product_name,
                            'score': score
                        })
            
            if not results:
                return None, None, None
            
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"搜索结果匹配得分:")
            for r in results[:5]:
                logger.info(f"  {r['model']}: 得分={r['score']}")
            
            best_match = results[0]
            
            if best_match['score'] < 50:
                logger.warning(f"最佳匹配得分过低: {best_match['model']} (得分={best_match['score']})")
                return None, None, None
            
            logger.info(f"选择最佳匹配: {best_match['model']} (得分={best_match['score']})")
            
            return best_match['url'], best_match['name'], best_match['model']
            
        except Exception as e:
            logger.error(f"搜索产品失败: {e}")
            return None, None, None
    
    def _get_product_features(self, session: requests.Session, product_url: str, model: str) -> Optional[ProductFeatures]:
        """获取产品特性"""
        try:
            response = session.get(product_url, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.request_delay)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            features = ProductFeatures(
                product_model=model,
                url=product_url,
                crawl_time=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            title_elem = soup.select_one('.product-intro h1, .product-name, h1.title')
            if title_elem:
                features.product_name = title_elem.get_text(strip=True)
            
            feature_div = soup.find('div', id='smbproductFeature')
            
            if feature_div:
                feature_items = feature_div.find_all('li')
                if not feature_items:
                    feature_items = feature_div.find_all('p')
                
                for item in feature_items:
                    text = item.get_text(strip=True)
                    if text:
                        features.features.append(text)
            else:
                alternative_selectors = [
                    'div.product-feature',
                    'div.feature-list',
                    '.product-intro ul',
                ]
                
                for selector in alternative_selectors:
                    feature_div = soup.select_one(selector)
                    if feature_div:
                        feature_items = feature_div.find_all('li')
                        if not feature_items:
                            feature_items = feature_div.find_all('p')
                        
                        for item in feature_items:
                            text = item.get_text(strip=True)
                            if text:
                                features.features.append(text)
                        break
            
            product_id_match = re.search(r'product_(\d+)', product_url)
            if product_id_match:
                features.product_id = int(product_id_match.group(1))
            
            logger.info(f"获取到 {len(features.features)} 条产品特性")
            return features
            
        except Exception as e:
            logger.error(f"获取产品特性失败: {e}")
            return None
    
    def crawl_by_product_id(self, product_id: int) -> Optional[ProductFeatures]:
        """
        根据产品ID爬取（每个线程独立session）
        
        Args:
            product_id: 产品ID
            
        Returns:
            ProductFeatures对象
        """
        url = self.product_url_template.format(id=product_id)
        session = self._create_session()
        
        try:
            response = session.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            feature_div = soup.find('div', id='smbproductFeature')
            if not feature_div:
                return None
            
            features = ProductFeatures(
                product_id=product_id,
                url=url,
                crawl_time=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            product_name_elem = soup.select_one('#smbproductName, .product-intro h1, .product-name, h1.title')
            if product_name_elem:
                features.product_name = product_name_elem.get_text(strip=True)
            
            product_model_elem = soup.select_one('#smbproductModel')
            if product_model_elem:
                features.product_model = product_model_elem.get_text(strip=True)
            else:
                model_patterns = [
                    r'(TL-[A-Z0-9\-]+)',
                    r'(SH[A-Z0-9\-]+)',
                    r'(SG[A-Z0-9\-]+)',
                    r'(TF-[A-Z0-9\-_]+)',
                    r'([A-Z]{2,}[0-9]{2,}[A-Z0-9\-_]*)',
                ]
                
                for pattern in model_patterns:
                    model_match = re.search(pattern, features.product_name + ' ' + url)
                    if model_match:
                        features.product_model = model_match.group(1)
                        break
            
            feature_items = feature_div.find_all('li')
            if not feature_items:
                feature_items = feature_div.find_all('p')
            
            for item in feature_items:
                text = item.get_text(strip=True)
                if text:
                    features.features.append(text)
            
            return features
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"产品ID {product_id} 请求失败: {e}")
            return None
        except Exception as e:
            logger.debug(f"产品ID {product_id} 解析失败: {e}")
            return None
        finally:
            session.close()
    
    def crawl_all_products(self, max_workers: int = None, 
                          progress_callback=None) -> List[ProductFeatures]:
        """
        爬取所有产品参数
        
        Args:
            max_workers: 并发线程数
            progress_callback: 进度回调函数 callback(current, total, product)
            
        Returns:
            产品特性列表
        """
        max_workers = max_workers or CRAWLER_CONFIG['concurrent_workers']
        max_id = self.max_product_id
        
        products = []
        total = max_id
        completed = 0
        
        logger.info(f"开始爬取产品参数，并发数: {max_workers}，总数: {max_id}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.crawl_by_product_id, i): i 
                for i in range(1, max_id + 1)
            }
            
            for future in as_completed(futures):
                product_id = futures[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result:
                        products.append(result)
                        
                        if progress_callback:
                            progress_callback(product_id, total, result)
                except Exception as e:
                    logger.debug(f"产品ID {product_id} 处理失败: {e}")
                
                if progress_callback and completed % 50 == 0:
                    progress_callback(completed, total, None)
        
        logger.info(f"爬取完成，共 {len(products)} 个产品")
        return products
    
    def close(self):
        """关闭会话"""
        pass
