def dummy_inference(img_bytes):
    """
    假模型，直接返回固定内容。
    可用你的AI推理代码替换。
    """
    return {
        "organ": "胰腺",
        "disease": "胰腺炎",
        "probability": 0.88,
        "suggestion": "建议进一步检查"
    }