# 胰腺诊断 AI Skill

## 接口路径
POST /diagnose

## 输入
- file：上传的B超图片（二进制）

## 输出
- organ: 器官名称
- disease: 疾病类别
- probability: 置信度分数（0-1）
- suggestion: 诊疗建议

## 调用示例

```sh
curl -X POST -F "file=@test.png" http://localhost:8000/diagnose
```