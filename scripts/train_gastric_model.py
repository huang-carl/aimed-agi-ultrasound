"""
胃部图像分类模型训练脚本
训练器官分类：胃 vs 胰腺
"""

import os
import sys
sys.path.insert(0, '/root/.openclaw/workspace')

from services.medical_image_trainer import MedicalImageTrainer

def main():
    print("=" * 60)
    print("胃部图像分类模型训练")
    print("=" * 60)
    
    trainer = MedicalImageTrainer()
    
    # 1. 收集标注图像
    print("\n【1. 收集标注图像】")
    labeled_data = trainer.collect_labeled_images()
    print(f"已收集标注图像：{len(labeled_data)} 张")
    
    if len(labeled_data) < 10:
        print("⚠️ 数据量不足，需要至少 10 张标注图像")
        return
    
    # 2. 生成训练清单
    print("\n【2. 生成训练清单】")
    manifest_path = trainer.generate_training_manifest()
    print(f"训练清单已生成：{manifest_path}")
    
    # 3. 准备训练数据
    print("\n【3. 训练数据状态】")
    training_data = trainer.prepare_training_data()
    print(f"状态：{training_data.get('status')}")
    print(f"总数：{len(labeled_data)}")
    
    # 4. 统计分布
    print("\n【4. 数据分布】")
    organ_count = {}
    for item in labeled_data:
        organ = item.get('organ', 'unknown')
        organ_count[organ] = organ_count.get(organ, 0) + 1
    
    for organ, count in organ_count.items():
        print(f"  {organ}: {count} 张")
    
    # 5. 检查是否可训练
    print("\n【5. 训练就绪检查】")
    if len(labeled_data) >= 10:
        print("✅ 数据量充足，可以开始训练")
        print("\n【下一步】")
        print("运行以下命令开始训练：")
        print("  cd /root/.openclaw/workspace")
        print("  python3 training/train_model.py")
    else:
        print("⚠️ 数据量不足，需要继续收集")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
