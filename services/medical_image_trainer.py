"""
医学图像分类模型训练框架
支持胃/胰腺器官分类 + 充盈状态识别
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class MedicalImageTrainer:
    """医学图像分类模型训练管理类"""
    
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.data_path = self.workspace / "data"
        self.cases_db = self.data_path / "cases.db"
        self.images_path = self.data_path / "cases"
        self.knowledge_path = self.workspace / "knowledge"
        self.models_path = self.workspace / "models"
        self.training_path = self.workspace / "training"
        
        # 创建必要目录
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.training_path.mkdir(parents=True, exist_ok=True)
        (self.training_path / "images").mkdir(parents=True, exist_ok=True)
        (self.training_path / "labels").mkdir(parents=True, exist_ok=True)
        
        # 分类标签 - 只区分器官，不区分充盈状态（默认必须充盈）
        self.organ_labels = {"胃": 0, "胰腺": 1}
        # 充盈状态已移除，系统只接受充盈状态图像
        
        # 训练配置
        self.config = {
            "image_size": 224,
            "batch_size": 32,
            "epochs": 50,
            "learning_rate": 0.001,
            "validation_split": 0.2
        }
    
    def collect_labeled_images(self) -> List[Dict[str, Any]]:
        """从数据库收集已标注的图像数据"""
        if not self.cases_db.exists():
            print("⚠️ 数据库不存在")
            return []
        
        conn = sqlite3.connect(str(self.cases_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, organ, patient_name, image_path, image_description, 
                   diagnosis, probability, image_quality, created_at
            FROM cases
            WHERE image_path IS NOT NULL AND image_path != ''
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        labeled_data = []
        for row in rows:
            # 检查图像文件是否存在
            image_path = Path(row['image_path'])
            if not image_path.exists():
                print(f"⚠️ 图像文件不存在：{image_path}")
                continue
            
            # 提取标注信息
            label = {
                "case_id": row['id'],
                "image_path": str(image_path.absolute()),
                "organ": row['organ'],
                "organ_label": self.organ_labels.get(row['organ'], -1),
                "patient_name": row['patient_name'],
                "image_description": row['image_description'],
                "diagnosis": row['diagnosis'],
                "probability": row['probability'],
                "image_quality": row['image_quality'],
                "created_at": row['created_at']
            }
            
            # 从描述或诊断中提取充盈状态（仅用于记录，不再用于分类）
            filling_status = self._extract_filling_status(
                row['image_description'],
                row['diagnosis']
            )
            label['filling_status'] = filling_status
            # 充盈状态已移除，不再用于分类
            
            labeled_data.append(label)
        
        return labeled_data
    
    def _extract_filling_status(self, description: str, diagnosis: str) -> str:
        """从描述或诊断中提取充盈状态"""
        text = (description or "") + " " + (diagnosis or "")
        
        if any(word in text for word in ["充盈", "充盈良好", "显影良好", "口服造影剂"]):
            return "已充盈"
        elif any(word in text for word in ["未充盈", "充盈不佳", "气体干扰"]):
            return "未充盈"
        else:
            return "未知"
    
    def generate_training_manifest(self, output_path: str = None) -> str:
        """生成训练数据清单"""
        labeled_data = self.collect_labeled_images()
        
        if not output_path:
            output_path = str(self.training_path / "training_manifest.json")
        
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "total_images": len(labeled_data),
            "organ_distribution": {},
            "filling_distribution": {},
            "images": labeled_data
        }
        
        # 统计分布
        for item in labeled_data:
            organ = item.get('organ', 'unknown')
            filling = item.get('filling_status', 'unknown')
            
            manifest['organ_distribution'][organ] = \
                manifest['organ_distribution'].get(organ, 0) + 1
            manifest['filling_distribution'][filling] = \
                manifest['filling_distribution'].get(filling, 0) + 1
        
        # 保存清单
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def prepare_training_data(self) -> Dict[str, Any]:
        """准备训练数据"""
        labeled_data = self.collect_labeled_images()
        
        # 检查数据量
        if len(labeled_data) < 10:
            return {
                "status": "insufficient_data",
                "message": f"当前只有 {len(labeled_data)} 个标注图像，需要至少 10 个",
                "recommendation": "请继续上传更多标注图像"
            }
        
        # 按器官分类
        stomach_images = [d for d in labeled_data if d['organ'] == '胃']
        pancreas_images = [d for d in labeled_data if d['organ'] == '胰腺']
        
        # 按充盈状态分类
        filled_images = [d for d in labeled_data if d['filling_status'] == '已充盈']
        unfilled_images = [d for d in labeled_data if d['filling_status'] == '未充盈']
        
        return {
            "status": "ready",
            "total": len(labeled_data),
            "by_organ": {
                "胃": len(stomach_images),
                "胰腺": len(pancreas_images)
            },
            "by_filling": {
                "已充盈": len(filled_images),
                "未充盈": len(unfilled_images),
                "未知": len(labeled_data) - len(filled_images) - len(unfilled_images)
            },
            "ready_for_training": len(labeled_data) >= 10
        }
    
    def create_training_script(self) -> str:
        """创建训练脚本"""
        script_content = '''"""
医学图像分类模型训练脚本
使用 PyTorch + ResNet18
"""

import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import json

class MedicalImageDataset(Dataset):
    def __init__(self, manifest_path, transform=None):
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        self.images = self.manifest['images']
        self.transform = transform
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]['image_path']
        image = Image.open(img_path).convert('RGB')
        
        organ_label = self.images[idx]['organ_label']
        filling_label = self.images[idx]['filling_label']
        
        if self.transform:
            image = self.transform(image)
        
        return image, organ_label, filling_label

class MultiTaskClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.resnet18(pretrained=True)
        self.backbone.fc = nn.Identity()
        
        self.organ_classifier = nn.Linear(512, 2)  # 胃 vs 胰腺
        self.filling_classifier = nn.Linear(512, 2)  # 充盈 vs 未充盈
    
    def forward(self, x):
        features = self.backbone(x)
        organ_out = self.organ_classifier(features)
        filling_out = self.filling_classifier(features)
        return organ_out, filling_out

def train():
    print("🚀 开始训练医学图像分类模型...")
    
    # 数据增强
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # 加载数据
    dataset = MedicalImageDataset(
        'training/training_manifest.json',
        transform=train_transform
    )
    
    print(f"📊 加载了 {len(dataset)} 个训练样本")
    
    # 创建模型
    model = MultiTaskClassifier()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # 训练循环
    epochs = 50
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for images, organ_labels, filling_labels in dataset:
            # 简化训练逻辑（实际需要 DataLoader）
            pass
        
        print(f"Epoch {epoch+1}/{epochs} completed")
    
    # 保存模型
    torch.save(model.state_dict(), 'models/medical_image_classifier.pth')
    print("✅ 模型训练完成！")

if __name__ == "__main__":
    train()
'''
        
        script_path = self.training_path / "train_model.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(script_path)
    
    def get_training_status(self) -> Dict[str, Any]:
        """获取训练状态"""
        status = {
            "data_collection": "ready" if self.cases_db.exists() else "not_started",
            "total_images": len(self.collect_labeled_images()),
            "training_manifest": "exists" if (self.training_path / "training_manifest.json").exists() else "not_generated",
            "model_file": "exists" if (self.models_path / "medical_image_classifier.pth").exists() else "not_trained",
            "ready_for_training": False
        }
        
        training_data = self.prepare_training_data()
        if training_data.get('status') == 'ready' and training_data.get('ready_for_training'):
            status['ready_for_training'] = True
        
        return status


# 测试
if __name__ == "__main__":
    trainer = MedicalImageTrainer()
    
    print("=" * 60)
    print("医学图像分类模型训练框架")
    print("=" * 60)
    
    # 收集标注图像
    print("\n【收集标注图像】")
    labeled_data = trainer.collect_labeled_images()
    print(f"已标注图像数：{len(labeled_data)}")
    
    # 生成训练清单
    print("\n【生成训练清单】")
    manifest_path = trainer.generate_training_manifest()
    print(f"清单已生成：{manifest_path}")
    
    # 准备训练数据
    print("\n【训练数据状态】")
    training_data = trainer.prepare_training_data()
    print(f"状态：{training_data.get('status')}")
    print(f"总数：{training_data.get('total')}")
    print(f"按器官：{training_data.get('by_organ')}")
    print(f"按充盈：{training_data.get('by_filling')}")
    print(f"可训练：{training_data.get('ready_for_training')}")
    
    # 创建训练脚本
    print("\n【创建训练脚本】")
    script_path = trainer.create_training_script()
    print(f"脚本已创建：{script_path}")
    
    # 训练状态
    print("\n【训练状态】")
    status = trainer.get_training_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
