"""
病例数据库管理模块
支持 SQLite 本地存储 + 阿里云 OSS 云存储
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class CaseDatabase:
    """病例数据库管理类"""
    
    def __init__(self, db_path: str = "/root/.openclaw/workspace/data/cases.db"):
        """
        初始化数据库
        
        Args:
            db_path: SQLite 数据库路径
        """
        self.db_path = db_path
        self.storage_path = Path("/root/.openclaw/workspace/data/cases")
        
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 病例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                patient_name TEXT,
                organ TEXT,
                image_path TEXT,
                oss_url TEXT,
                image_description TEXT,
                diagnosis TEXT,
                probability REAL,
                image_quality TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 分类索引表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                category_name TEXT,
                organ TEXT,
                date TEXT,
                case_ids TEXT,
                case_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_organ ON cases(organ)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON cases(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON cases(created_at)')
        
        conn.commit()
        conn.close()
    
    def add_case(self, case_data: Dict[str, Any]) -> str:
        """
        添加新病例
        
        Args:
            case_data: 病例数据字典
            
        Returns:
            病例 ID
        """
        case_id = f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cases (
                id, patient_id, patient_name, organ, image_path, oss_url,
                image_description, diagnosis, probability, image_quality,
                category, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            case_id,
            case_data.get('patient_id', ''),
            case_data.get('patient_name', ''),
            case_data.get('organ', ''),
            case_data.get('image_path', ''),
            case_data.get('oss_url', ''),
            case_data.get('image_description', ''),
            case_data.get('diagnosis', ''),
            case_data.get('probability', 0.0),
            case_data.get('image_quality', 'fair'),
            case_data.get('category', ''),
            case_data.get('created_at', datetime.now().isoformat()),
            case_data.get('updated_at', datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        # 更新分类统计
        self._update_category(case_data.get('organ', ''), case_data.get('category', ''), case_id)
        
        return case_id
    
    def _update_category(self, organ: str, category: str, case_id: str):
        """更新分类统计"""
        if not organ or not category:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 尝试获取现有分类
        category_id = f"cat_{organ}_{category}"
        cursor.execute('SELECT case_ids, case_count FROM categories WHERE id = ?', (category_id,))
        row = cursor.fetchone()
        
        if row:
            case_ids = json.loads(row[0])
            case_ids.append(case_id)
            case_count = row[1] + 1
            cursor.execute('''
                UPDATE categories SET case_ids = ?, case_count = ?, updated_at = ?
                WHERE id = ?
            ''', (json.dumps(case_ids), case_count, datetime.now().isoformat(), category_id))
        else:
            cursor.execute('''
                INSERT INTO categories (id, category_name, organ, date, case_ids, case_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category_id, category, organ, category, json.dumps([case_id]), 1))
        
        conn.commit()
        conn.close()
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """获取单个病例"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_cases_by_organ(self, organ: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按器官获取病例列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cases WHERE organ = ? ORDER BY created_at DESC LIMIT ?
        ''', (organ, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_cases_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类获取病例列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cases WHERE category = ? ORDER BY created_at DESC
        ''', (category,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总病例数
        cursor.execute('SELECT COUNT(*) FROM cases')
        total_cases = cursor.fetchone()[0]
        
        # 按器官统计
        cursor.execute('SELECT organ, COUNT(*) FROM cases GROUP BY organ')
        organ_stats = dict(cursor.fetchall())
        
        # 按分类统计
        cursor.execute('SELECT category, COUNT(*) FROM cases GROUP BY category')
        category_stats = dict(cursor.fetchall())
        
        # 最近添加的病例
        cursor.execute('''
            SELECT id, organ, diagnosis, created_at FROM cases 
            ORDER BY created_at DESC LIMIT 5
        ''')
        recent_cases = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_cases': total_cases,
            'organ_stats': organ_stats,
            'category_stats': category_stats,
            'recent_cases': [
                {'id': r[0], 'organ': r[1], 'diagnosis': r[2], 'created_at': r[3]}
                for r in recent_cases
            ]
        }
    
    def export_report(self, output_path: str = None) -> str:
        """
        导出病例报告（JSON 格式）
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        if not output_path:
            output_path = f"/root/.openclaw/workspace/data/cases_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        stats = self.get_statistics()
        stats['exported_at'] = datetime.now().isoformat()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def list_all_cases(self) -> List[Dict[str, Any]]:
        """列出所有病例"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cases ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# 测试
if __name__ == "__main__":
    db = CaseDatabase()
    
    print("=" * 60)
    print("病例数据库测试")
    print("=" * 60)
    
    # 添加测试病例
    test_case = {
        'patient_id': 'P001',
        'patient_name': '测试患者',
        'organ': '胃',
        'image_path': '/data/cases/stomach/2026-04-22/case_001.jpg',
        'oss_url': '',
        'image_description': '胃窦部黏膜充血水肿，可见点状糜烂',
        'diagnosis': '慢性胃炎',
        'probability': 0.85,
        'image_quality': 'good',
        'category': '2026-04-22'
    }
    
    case_id = db.add_case(test_case)
    print(f"✅ 添加病例：{case_id}")
    
    # 获取统计
    stats = db.get_statistics()
    print(f"\n📊 统计信息:")
    print(f"   总病例数：{stats['total_cases']}")
    print(f"   器官分布：{stats['organ_stats']}")
    print(f"   分类统计：{stats['category_stats']}")
    
    # 导出报告
    report_path = db.export_report()
    print(f"\n📄 报告已导出：{report_path}")
    
    print("\n" + "=" * 60)
