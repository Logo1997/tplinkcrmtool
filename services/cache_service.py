# -*- coding: utf-8 -*-
"""
产品参数缓存服务
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from config import STORAGE_CONFIG
from models import ProductFeatures
from services.crawler_service import CrawlerService

logger = logging.getLogger(__name__)


class CacheService:
    """产品参数缓存服务"""
    
    FOCAL_LENGTH_SUFFIXES = ['2.8', '4', '6', '8', '12', '16', '2.8mm', '4mm', '6mm', '8mm', '12mm', '16mm']
    
    def __init__(self):
        self.cache_file = STORAGE_CONFIG['cache_file']
        self.data_dir = STORAGE_CONFIG['data_dir']
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self._cache: Dict = {}
        self._model_to_id: Dict[str, int] = {}
        self._loaded = False
    
    def _normalize_model(self, model: str) -> str:
        """
        规范化型号，去除焦距后缀
        
        TL-IPC445GP-2.8 -> TL-IPC445GP
        TL-IPC445GP-4 -> TL-IPC445GP
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
    
    def _calculate_match_score(self, crm_model: str, cache_model: str) -> int:
        """
        计算型号匹配得分
        
        Args:
            crm_model: CRM中的产品型号
            cache_model: 缓存中的产品型号
            
        Returns:
            匹配得分，越高越匹配
        """
        if not crm_model or not cache_model:
            return 0
        
        crm_upper = crm_model.upper().strip()
        cache_upper = cache_model.upper().strip()
        
        if crm_upper == cache_upper:
            return 100
        
        crm_normalized = self._normalize_model(crm_upper)
        cache_normalized = self._normalize_model(cache_upper)
        
        if crm_normalized == cache_normalized:
            return 90
        
        if crm_normalized == cache_upper:
            return 85
        
        if cache_normalized.startswith(crm_normalized):
            return 80
        
        if crm_normalized.startswith(cache_normalized):
            return 75
        
        crm_base = re.sub(r'[\-_].*$', '', crm_normalized)
        cache_base = re.sub(r'[\-_].*$', '', cache_normalized)
        
        if crm_base and cache_base and crm_base == cache_base:
            return 70
        
        if crm_normalized in cache_normalized:
            return 60
        
        if cache_normalized in crm_normalized:
            return 50
        
        return 0
    
    def load(self) -> bool:
        """加载缓存"""
        if not self.cache_file.exists():
            logger.info("缓存文件不存在")
            return False
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._cache = data.get('products', {})
            self._model_to_id = data.get('model_to_id', {})
            self._loaded = True
            
            logger.info(f"加载缓存成功，共 {len(self._cache)} 个产品")
            return True
            
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            return False
    
    def save(self):
        """保存缓存"""
        try:
            data = {
                'cache_version': '1.0',
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_products': len(self._cache),
                'valid_ids': list(set(
                    self._cache[m].get('product_id', 0) 
                    for m in self._cache if self._cache[m].get('product_id')
                )),
                'products': self._cache,
                'model_to_id': self._model_to_id,
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"缓存保存成功，共 {len(self._cache)} 个产品")
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def get(self, model: str) -> Optional[ProductFeatures]:
        """
        获取产品参数
        
        优先级：
        1. 精确匹配
        2. 规范化后匹配（处理焦距后缀）
        3. 模糊匹配（得分>=70）
        
        Args:
            model: 产品型号
            
        Returns:
            ProductFeatures对象，未找到返回None
        """
        if not self._loaded:
            self.load()
        
        if not model:
            return None
        
        model_upper = model.upper().strip()
        
        if model_upper in self._cache:
            data = self._cache[model_upper]
            logger.info(f"缓存精确匹配: {model}")
            return ProductFeatures.from_dict(data)
        
        normalized_model = self._normalize_model(model)
        
        if normalized_model in self._cache:
            data = self._cache[normalized_model]
            logger.info(f"缓存规范化匹配: {model} -> {normalized_model}")
            return ProductFeatures.from_dict(data)
        
        best_match = None
        best_score = 0
        
        for cache_model in self._cache.keys():
            score = self._calculate_match_score(model, cache_model)
            if score > best_score:
                best_score = score
                best_match = cache_model
        
        if best_match and best_score >= 70:
            data = self._cache[best_match]
            logger.info(f"缓存模糊匹配: {model} -> {best_match} (得分={best_score})")
            return ProductFeatures.from_dict(data)
        
        logger.info(f"缓存未找到匹配: {model}")
        return None
    
    def set(self, features: ProductFeatures):
        """设置产品参数缓存"""
        if not features.product_model:
            return
        
        model_upper = features.product_model.upper()
        self._cache[model_upper] = features.to_dict()
        
        if features.product_id:
            self._model_to_id[model_upper] = features.product_id
    
    def has_cache(self) -> bool:
        """是否有缓存"""
        return self.cache_file.exists() and len(self._cache) > 0
    
    def get_cache_info(self) -> dict:
        """获取缓存信息"""
        if not self.cache_file.exists():
            return {
                'exists': False,
                'total': 0,
                'last_update': '',
            }
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'exists': True,
                'total': data.get('total_products', 0),
                'last_update': data.get('last_update', ''),
            }
        except Exception:
            return {
                'exists': False,
                'total': 0,
                'last_update': '',
            }
    
    def update_cache(self, progress_callback=None) -> int:
        """
        更新缓存（全量爬取）
        
        Args:
            progress_callback: 进度回调
            
        Returns:
            更新的产品数量
        """
        crawler = CrawlerService()
        
        def on_progress(current, total, product):
            if product:
                self.set(product)
            
            if progress_callback:
                progress_callback(current, total, product)
        
        products = crawler.crawl_all_products(progress_callback=on_progress)
        
        for product in products:
            self.set(product)
        
        self.save()
        crawler.close()
        
        return len(products)
    
    def clear(self):
        """清空缓存"""
        self._cache = {}
        self._model_to_id = {}
        self._loaded = False
        
        if self.cache_file.exists():
            self.cache_file.unlink()
        
        logger.info("缓存已清空")
