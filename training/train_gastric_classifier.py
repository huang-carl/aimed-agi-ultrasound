"""
胃部图像分类模型训练脚本
使用 PyTorch + ResNet18 进行器官分类
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from datetime import datetime

# 配置
DATA_DIR = '/root/.openclaw/workspace/data/cases'
MANIFEST_PATH = '/root/.openclaw/workspace/training/training_manifest.json'
MODEL_DIR = '/root/.openclaw/workspace/models'
MODEL_PATH = os.path.join(MODEL_DIR, 'gastric_classifier.pth')

# 确保模型目录存在
os.makedirs(MODEL_DIR, exist_ok=True)

class GastricImageDataset(Dataset):
    """胃部图像数据集"""
    def __init__(self, manifest_path, transform=None):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        self.images = self.manifest['images']
        self.transform = transform
        
        # 创建器官标签映射
        self.organ_to_label = {'胃': 0, '胰腺': 1}
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]['image_path']
        image = Image.open(img_path).convert('RGB')
        
        organ = self.images[idx]['organ']
        label = self.organ_to_label.get(organ, 0)
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class GastricClassifier(nn.Module):
    """胃部图像分类器"""
    def __init__(self, num_classes=2):
        super().__init__()
        # 使用预训练的 ResNet18
        self.backbone = models.resnet18(pretrained=True)
        # 修改最后的全连接层
        self.backbone.fc = nn.Linear(512, num_classes)
    
    def forward(self, x):
        return self.backbone(x)

def train():
    print("=" * 60)
    print("胃部图像分类模型训练")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n【1. 加载数据】")
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = GastricImageDataset(MANIFEST_PATH, transform=train_transform)
    print(f"数据集大小：{len(dataset)} 张图像")
    
    if len(dataset) < 10:
        print("⚠️ 数据量不足，需要至少 10 张图像")
        return
    
    # 创建数据加载器
    batch_size = min(16, len(dataset))
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # 2. 创建模型
    print("\n【2. 创建模型】")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备：{device}")
    
    model = GastricClassifier(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # 3. 训练循环
    print("\n【3. 开始训练】")
    epochs = 30
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)
            
            # 前向传播
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        # 打印进度
        avg_loss = total_loss / len(data_loader)
        accuracy = 100 * correct / total
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.1f}%")
    
    # 4. 保存模型
    print("\n【4. 保存模型】")
    torch.save({
        'epoch': epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': avg_loss,
        'accuracy': accuracy,
    }, MODEL_PATH)
    
    print(f"✅ 模型已保存到：{MODEL_PATH}")
    print(f"   最终准确率：{accuracy:.1f}%")
    print(f"   最终损失：{avg_loss:.4f}")
    
    # 5. 创建模型信息文件
    info_path = MODEL_PATH.replace('.pth', '_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({
            'model_type': 'gastric_classifier',
            'architecture': 'ResNet18',
            'num_classes': 2,
            'classes': ['胃', '胰腺'],
            'training_date': datetime.now().isoformat(),
            'training_samples': len(dataset),
            'final_accuracy': accuracy,
            'final_loss': avg_loss,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 模型信息已保存到：{info_path}")
    
    print("\n" + "=" * 60)
    print("训练完成！")
    print("=" * 60)

if __name__ == "__main__":
    train()
