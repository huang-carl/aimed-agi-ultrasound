# 测试样本说明

本目录用于存放测试用的超声影像样本。

---

## 📁 目录结构

```
samples/
├── stomach/           # 胃部样本
│   ├── normal/        # 正常胃影像
│   └── abnormal/      # 异常胃影像（胃炎、溃疡等）
├── pancreas/          # 胰腺样本
│   ├── normal/        # 正常胰腺影像
│   └── abnormal/      # 异常胰腺影像（胰腺炎、肿瘤等）
└── README.md          # 本文件
```

---

## 📊 样本要求

### 图像格式

- **支持格式：** PNG, JPG, DICOM (.dcm)
- **推荐分辨率：** 512x512 或更高
- **文件大小：** < 10MB
- **色彩模式：** 灰度图（单通道）

### 命名规范

```
{器官}_{状态}_{序号}.{扩展名}

示例：
- stomach_normal_001.png
- stomach_abnormal_gastritis_001.png
- pancreas_normal_001.png
- pancreas_abnormal_tumor_001.png
```

### 数据脱敏

- ✅ 移除患者姓名、ID 等个人信息
- ✅ 移除医院名称、设备序列号
- ✅ 保留必要的医学元数据（成像参数等）

---

## 📥 获取测试样本

### 方式一：使用公开数据集

1. **Ultrasound Nerve Segmentation** (Kaggle)
   - https://www.kaggle.com/c/ultrasound-nerve-segmentation
   - 包含神经超声图像

2. **Medical Decathlon**
   - http://medicaldecathlon.com/
   - 多器官医学影像数据集

### 方式二：合成数据

使用数据增强工具生成合成样本：

```python
from PIL import Image
import numpy as np

# 示例：生成测试用灰度图
image = np.random.randint(0, 255, (512, 512), dtype=np.uint8)
Image.fromarray(image).save("stomach_normal_001.png")
```

### 方式三：医院合作数据

与医院合作获取真实脱敏数据（需伦理审批）。

---

## 🧪 使用样本测试

### 测试胃诊断

```bash
curl -X POST "http://localhost:8000/api/stomach/diagnose" \
  -F "file=@samples/stomach/normal/stomach_normal_001.png"
```

### 测试胰腺诊断

```bash
curl -X POST "http://localhost:8000/api/pancreas/diagnose" \
  -F "file=@samples/pancreas/normal/pancreas_normal_001.png"
```

---

## 📋 样本清单（待补充）

| 器官 | 状态 | 数量 | 格式 | 来源 |
|------|------|------|------|------|
| 胃 | 正常 | 0 | - | - |
| 胃 | 异常 | 0 | - | - |
| 胰腺 | 正常 | 0 | - | - |
| 胰腺 | 异常 | 0 | - | - |

**总计：** 0 个样本

---

## ⚠️ 注意事项

1. **隐私保护：** 确保所有样本已完全脱敏
2. **版权合规：** 使用公开数据集需遵守相应协议
3. **伦理审批：** 临床数据需通过伦理审查
4. **数据安全：** 样本目录已在 .gitignore 中，不会提交到 Git

---

## 📞 联系

如需测试样本支持，请联系：

- **邮箱：** aimed@aius.xin
- **GitHub Issues:** https://github.com/huang-carl/aimed-agi-ultrasound/issues

---

**最后更新：** 2026-04-18
