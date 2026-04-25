"""
图像分割服务 - SAM (Segment Anything Model)
用于超声图像分割和分析
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    import torch
    import torchvision
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False

try:
    import numpy as np
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageSegmentationService:
    """图像分割服务（SAM 模型）"""
    
    def __init__(self, model_type: str = "vit_h", checkpoint_path: Optional[str] = None):
        """
        初始化图像分割服务
        
        Args:
            model_type: SAM 模型类型（vit_h/vit_l/vit_b）
            checkpoint_path: 模型权重路径（可选，自动下载）
        """
        if not SAM_AVAILABLE:
            raise ImportError("SAM 库未安装: pip install segment-anything torch torchvision")
        
        self.model_type = model_type
        self.checkpoint_path = checkpoint_path or self._get_default_checkpoint()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 加载模型
        self.sam = None
        self.predictor = None
        self.mask_generator = None
        self._load_model()
        
        print(f"[图像分割] 初始化完成 - 模型: {model_type}, 设备: {self.device}")
    
    def _get_default_checkpoint(self) -> str:
        """获取默认模型权重路径"""
        cache_dir = os.path.expanduser("~/.cache/segment_anything")
        os.makedirs(cache_dir, exist_ok=True)
        
        checkpoints = {
            "vit_h": os.path.join(cache_dir, "sam_vit_h_4b8939.pth"),
            "vit_l": os.path.join(cache_dir, "sam_vit_l_0b3195.pth"),
            "vit_b": os.path.join(cache_dir, "sam_vit_b_01ec64.pth"),
        }
        return checkpoints.get(self.model_type, checkpoints["vit_h"])
    
    def _load_model(self):
        """加载 SAM 模型"""
        print(f"[SAM] 加载模型: {self.model_type}")
        print(f"[SAM] 权重路径: {self.checkpoint_path}")
        
        if not os.path.exists(self.checkpoint_path):
            print(f"[SAM] 警告: 权重文件不存在，需要下载")
            print(f"[SAM] 下载地址: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth")
            # 创建占位模型（实际使用时需要下载权重）
            self.sam = None
            return
        
        try:
            self.sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
            self.sam.to(device=self.device)
            self.predictor = SamPredictor(self.sam)
            self.mask_generator = SamAutomaticMaskGenerator(self.sam)
            print(f"[SAM] 模型加载成功")
        except Exception as e:
            print(f"[SAM] 模型加载失败: {e}")
            self.sam = None
    
    def segment_image(self, image_path: str, point_coords: Optional[List] = None, 
                     point_labels: Optional[List] = None, 
                     box: Optional[List] = None) -> Dict[str, Any]:
        """
        分割图像
        
        Args:
            image_path: 图像路径
            point_coords: 提示点坐标 [[x, y], ...]
            point_labels: 提示点标签 [1=前景, 0=背景]
            box: 边界框 [x1, y1, x2, y2]
            
        Returns:
            分割结果
        """
        if not self.sam:
            return {"success": False, "error": "SAM 模型未加载"}
        
        if not PIL_AVAILABLE:
            return {"success": False, "error": "PIL 库未安装"}
        
        try:
            # 加载图像
            image = Image.open(image_path).convert("RGB")
            image_np = np.array(image)
            
            # 设置图像
            self.predictor.set_image(image_np)
            
            # 执行分割
            masks, scores, logits = self._run_segmentation(point_coords, point_labels, box)
            
            # 分析结果
            result = self._analyze_masks(masks, scores, image_np)
            result['success'] = True
            result['image_path'] = image_path
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_segmentation(self, point_coords, point_labels, box):
        """执行分割"""
        if point_coords:
            # 点提示分割
            point_coords = np.array(point_coords)
            point_labels = np.array(point_labels) if point_labels else np.ones(len(point_coords))
            masks, scores, logits = self.predictor.predict(
                point_coords=point_coords,
                point_labels=point_labels,
                multimask_output=True
            )
        elif box:
            # 框提示分割
            box = np.array(box)
            masks, scores, logits = self.predictor.predict(
                point_coords=None,
                point_labels=None,
                box=box[None, :],
                multimask_output=True
            )
        else:
            # 自动分割
            masks = self.mask_generator.generate(np.array(Image.open(self.predictor.image).convert("RGB")))
            scores = [m.get('predicted_iou', 0) for m in masks]
            masks = [m['segmentation'] for m in masks]
        
        return masks, scores, logits
    
    def _analyze_masks(self, masks, scores, image_np) -> Dict[str, Any]:
        """分析分割结果"""
        analysis = {
            'mask_count': len(masks) if isinstance(masks, list) else 1,
            'top_scores': [],
            'mask_areas': [],
            'image_shape': image_np.shape
        }
        
        # 计算每个掩码的面积和得分
        if isinstance(masks, list) and len(masks) > 0:
            for i, mask in enumerate(masks):
                area = np.sum(mask)
                total_pixels = mask.shape[0] * mask.shape[1]
                coverage = area / total_pixels if total_pixels > 0 else 0
                
                analysis['mask_areas'].append({
                    'index': i,
                    'area': int(area),
                    'coverage': round(coverage, 4),
                    'score': float(scores[i]) if i < len(scores) else 0
                })
            
            # 按得分排序
            analysis['mask_areas'].sort(key=lambda x: x['score'], reverse=True)
            analysis['top_scores'] = [m['score'] for m in analysis['mask_areas'][:3]]
        
        return analysis
    
    def auto_segment(self, image_path: str, min_area: int = 100, max_area: int = None) -> Dict[str, Any]:
        """
        自动分割（无需提示）
        
        Args:
            image_path: 图像路径
            min_area: 最小掩码面积
            max_area: 最大掩码面积
            
        Returns:
            分割结果
        """
        if not self.mask_generator:
            return {"success": False, "error": "SAM 自动分割器未初始化"}
        
        try:
            image = Image.open(image_path).convert("RGB")
            image_np = np.array(image)
            
            # 自动分割
            masks = self.mask_generator.generate(image_np)
            
            # 过滤掩码
            if min_area or max_area:
                masks = [
                    m for m in masks 
                    if (not min_area or m['area'] >= min_area) and 
                       (not max_area or m['area'] <= max_area)
                ]
            
            # 分析结果
            result = {
                'success': True,
                'image_path': image_path,
                'mask_count': len(masks),
                'masks': [],
                'timestamp': datetime.now().isoformat()
            }
            
            for i, mask in enumerate(masks[:10]):  # 只返回前 10 个
                result['masks'].append({
                    'index': i,
                    'area': mask.get('area', 0),
                    'score': float(mask.get('predicted_iou', 0)),
                    'stability_score': float(mask.get('stability_score', 0))
                })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'model_type': self.model_type,
            'device': self.device,
            'cuda_available': torch.cuda.is_available(),
            'checkpoint_path': self.checkpoint_path,
            'checkpoint_exists': os.path.exists(self.checkpoint_path) if self.checkpoint_path else False,
            'model_loaded': self.sam is not None
        }


# 便捷函数
def create_segmentation_service(model_type: str = "vit_b") -> ImageSegmentationService:
    """创建图像分割服务实例"""
    return ImageSegmentationService(model_type=model_type)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("图像分割服务测试")
    print("=" * 60)
    
    if SAM_AVAILABLE:
        print("\n【测试 SAM】")
        service = ImageSegmentationService(model_type="vit_b")
        
        # 获取模型信息
        info = service.get_model_info()
        print(f"模型类型: {info['model_type']}")
        print(f"设备: {info['device']}")
        print(f"CUDA: {info['cuda_available']}")
        print(f"模型已加载: {info['model_loaded']}")
        
        if info['checkpoint_exists']:
            print("✅ 权重文件存在")
        else:
            print("⚠️ 权重文件不存在，需要下载")
            print("   下载命令:")
            print("   wget -O ~/.cache/segment_anything/sam_vit_b_01ec64.pth \\")
            print("     https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth")
    else:
        print("❌ SAM 库未安装")
    
    print("\n" + "=" * 60)
