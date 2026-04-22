"""
同步文件系统图像到数据库
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

def sync_images_to_db():
    db_path = '/root/.openclaw/workspace/data/cases.db'
    images_dir = Path('/root/.openclaw/workspace/data/cases/stomach/2026-04-23')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取已有记录
    cursor.execute('SELECT image_path FROM cases')
    existing_paths = set(row[0] for row in cursor.fetchall())
    
    # 遍历文件系统
    added_count = 0
    for img_file in images_dir.glob('*.jpg'):
        img_path = str(img_file.absolute())
        
        if img_path in existing_paths:
            continue
        
        # 从文件名提取诊断信息
        filename = img_file.stem
        diagnosis = filename.split('_')[0] if '_' in filename else filename
        
        # 插入数据库
        case_id = f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        cursor.execute('''
            INSERT INTO cases (id, organ, patient_name, image_path, diagnosis, image_quality, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (case_id, '胃', '未知', img_path, diagnosis, 'good', datetime.now().strftime('%Y-%m-%d')))
        
        added_count += 1
        if added_count % 10 == 0:
            print(f"已添加 {added_count} 张图像...")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 同步完成！新增 {added_count} 张图像")

if __name__ == "__main__":
    sync_images_to_db()
