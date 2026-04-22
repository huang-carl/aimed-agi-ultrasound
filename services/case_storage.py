"""
病例图像存储管理
支持本地存储 + 阿里云 OSS 云存储
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class CaseStorage:
    """病例图像存储管理类"""
    
    def __init__(self, base_path: str = "/root/.openclaw/workspace/data/cases"):
        """
        初始化存储路径
        
        Args:
            base_path: 基础存储路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 阿里云 OSS 配置（可选）
        self.oss_enabled = os.getenv('ALIYUN_OSS_ENABLED', 'false').lower() == 'true'
        self.oss_bucket = os.getenv('ALIYUN_OSS_BUCKET', '')
        self.oss_endpoint = os.getenv('ALIYUN_OSS_ENDPOINT', '')
        self.oss_access_key = os.getenv('ALIYUN_ACCESS_KEY_ID', '')
        self.oss_access_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')
        
        if self.oss_enabled:
            self._init_oss()
    
    def _init_oss(self):
        """初始化阿里云 OSS 客户端"""
        try:
            import oss2
            auth = oss2.Auth(self.oss_access_key, self.oss_access_secret)
            self.oss_bucket = oss2.Bucket(auth, self.oss_endpoint, self.oss_bucket)
            print("✅ 阿里云 OSS 初始化成功")
        except Exception as e:
            print(f"⚠️ 阿里云 OSS 初始化失败：{e}，将使用本地存储")
            self.oss_enabled = False
    
    def save_image(self, image_data: bytes, organ: str, case_id: str, 
                   filename: str = None) -> Dict[str, str]:
        """
        保存病例图像
        
        Args:
            image_data: 图像二进制数据
            organ: 器官类型（胃/胰腺）
            case_id: 病例 ID
            filename: 文件名（可选）
            
        Returns:
            存储路径信息
        """
        # 生成存储路径
        date_str = datetime.now().strftime('%Y-%m-%d')
        organ_dir = 'stomach' if organ == '胃' else 'pancreas'
        
        save_dir = self.base_path / organ_dir / date_str
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        if not filename:
            ext = '.jpg'  # 默认扩展名
            filename = f"{case_id}{ext}"
        
        file_path = save_dir / filename
        
        # 保存本地文件
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        result = {
            'local_path': str(file_path.absolute()),
            'relative_path': f"{organ_dir}/{date_str}/{filename}",
            'oss_url': ''
        }
        
        # 上传到 OSS（如果启用）
        if self.oss_enabled:
            try:
                oss_key = f"cases/{organ_dir}/{date_str}/{filename}"
                self.oss_bucket.put_object(oss_key, image_data)
                result['oss_url'] = f"https://{self.oss_bucket.bucket_name}.{self.oss_endpoint}/{oss_key}"
            except Exception as e:
                print(f"⚠️ OSS 上传失败：{e}")
        
        return result
    
    def save_image_from_file(self, source_path: str, organ: str, case_id: str,
                             filename: str = None) -> Dict[str, str]:
        """
        从现有文件保存病例图像
        
        Args:
            source_path: 源文件路径
            organ: 器官类型
            case_id: 病例 ID
            filename: 文件名
            
        Returns:
            存储路径信息
        """
        with open(source_path, 'rb') as f:
            image_data = f.read()
        
        return self.save_image(image_data, organ, case_id, filename)
    
    def get_image_path(self, organ: str, date_str: str, filename: str) -> Optional[str]:
        """
        获取图像本地路径
        
        Args:
            organ: 器官类型
            date_str: 日期字符串
            filename: 文件名
            
        Returns:
            文件路径（如果存在）
        """
        organ_dir = 'stomach' if organ == '胃' else 'pancreas'
        file_path = self.base_path / organ_dir / date_str / filename
        
        if file_path.exists():
            return str(file_path.absolute())
        return None
    
    def delete_case(self, organ: str, date_str: str, filename: str) -> bool:
        """
        删除病例图像
        
        Args:
            organ: 器官类型
            date_str: 日期字符串
            filename: 文件名
            
        Returns:
            是否成功删除
        """
        local_path = self.get_image_path(organ, date_str, filename)
        
        if not local_path:
            return False
        
        try:
            # 删除本地文件
            os.remove(local_path)
            
            # 删除 OSS 文件（如果存在）
            if self.oss_enabled:
                organ_dir = 'stomach' if organ == '胃' else 'pancreas'
                oss_key = f"cases/{organ_dir}/{date_str}/{filename}"
                self.oss_bucket.delete_object(oss_key)
            
            return True
        except Exception as e:
            print(f"删除失败：{e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        stats = {
            'total_size_mb': 0,
            'file_count': 0,
            'by_organ': {}
        }
        
        for organ_dir in ['stomach', 'pancreas']:
            organ_path = self.base_path / organ_dir
            if organ_path.exists():
                organ_size = 0
                organ_count = 0
                
                for root, dirs, files in os.walk(organ_path):
                    for file in files:
                        file_path = Path(root) / file
                        organ_size += file_path.stat().st_size
                        organ_count += 1
                
                organ_name = '胃' if organ_dir == 'stomach' else '胰腺'
                stats['by_organ'][organ_name] = {
                    'count': organ_count,
                    'size_mb': round(organ_size / 1024 / 1024, 2)
                }
                
                stats['total_size_mb'] += organ_size / 1024 / 1024
                stats['file_count'] += organ_count
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        stats['oss_enabled'] = self.oss_enabled
        stats['base_path'] = str(self.base_path.absolute())
        
        return stats


# 测试
if __name__ == "__main__":
    storage = CaseStorage()
    
    print("=" * 60)
    print("病例图像存储测试")
    print("=" * 60)
    
    # 获取存储统计
    stats = storage.get_storage_stats()
    print(f"\n📊 存储统计:")
    print(f"   基础路径：{stats['base_path']}")
    print(f"   总文件数：{stats['file_count']}")
    print(f"   总大小：{stats['total_size_mb']} MB")
    print(f"   按器官:")
    for organ, data in stats['by_organ'].items():
        print(f"      {organ}: {data['count']} 个文件，{data['size_mb']} MB")
    print(f"   OSS 启用：{stats['oss_enabled']}")
    
    print("\n" + "=" * 60)
