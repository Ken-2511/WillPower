# 屏幕截图内容分析 - 完整指南

这里提供多种低成本的屏幕截图分析方案，从完全免费到极低成本的付费API。

## 🚀 快速开始

### 1. 完全免费方案（推荐新手）

#### Option A: Ollama + LLaVA（最佳免费方案）
```bash
# 1. 安装Ollama
# 访问 https://ollama.ai/ 下载安装

# 2. 下载LLaVA模型
ollama pull llava:7b

# 3. 测试
python analysis/local_analyzer.py
```

**优点**: 效果接近GPT-4V，完全免费，支持中文
**缺点**: 需要显卡（4GB显存），首次下载4GB模型

#### Option B: BLIP-2（轻量级）
```bash
# 安装依赖
pip install transformers torch torchvision Pillow

# 直接运行
python -c "from analysis.local_analyzer import LocalAnalyzer; analyzer = LocalAnalyzer(); print(analyzer.analyze_with_blip2('your_image.jpg'))"
```

**优点**: 轻量级，CPU可运行，速度快
**缺点**: 功能有限，不支持中文对话

### 2. 极低成本付费方案

#### Google Gemini Pro Vision（最便宜）
- **成本**: 约$0.0025/张图片
- **1000张图片**: 约$2.5
- 在 `analysis/screenshot_analyzer.py` 中配置API密钥

#### GPT-4V（效果最佳）
- **成本**: $0.01/张图片  
- **1000张图片**: 约$10
- 效果最佳，支持中文

## 📊 成本对比

运行成本计算器选择最适合的方案：
```bash
python analysis/cost_calculator.py
```

### 不同数量的成本对比

| 图片数量 | 免费方案(Ollama) | Gemini Pro | GPT-4V |
|---------|----------------|------------|--------|
| 100张    | $0            | $0.25      | $1.00  |
| 1000张   | $0            | $2.50      | $10.00 |
| 10000张  | $0            | $25.00     | $100.00|

## 🛠️ 使用方法

### 批量分析截图

1. **配置路径**（编辑 `analysis/config.py`）：
```python
SCREENSHOTS_PATH = r"D:\screenCap"  # 你的截图路径
DATE = "2024-01-15"  # 分析日期
OUTPUT_PATH = r"C:\Users\IWMAI\Desktop"  # 结果保存路径
```

2. **选择分析方案**：
```python
from analysis.screenshot_analyzer import ScreenshotAnalyzer

# 免费本地方案
analyzer = ScreenshotAnalyzer(model_type="local")

# 或者付费API方案
analyzer = ScreenshotAnalyzer(
    api_key="your_api_key", 
    model_type="gpt4v"  # 或 "gemini"
)

# 批量分析
results = analyzer.batch_analyze_screenshots(screenshots_dir, output_file)
```

3. **查看结果**：
分析结果保存为JSON格式，包含每张图片的详细分析。

## 🎯 方案选择建议

### 如果你有显卡（推荐）
1. **Ollama + LLaVA**: 完全免费，效果最佳
2. 备选：**InstructBLIP**: 可回答特定问题

### 如果只有CPU
1. **BLIP-2**: 轻量级，速度快
2. 备选：**Google Gemini**: 成本极低的云端方案

### 如果追求最佳效果
1. **GPT-4V**: 效果最佳，但成本较高
2. **Google Gemini Pro**: 性价比最高

### 预算考虑
- **$0预算**: Ollama + LLaVA 或 BLIP-2
- **$1-10预算**: Google Gemini Pro（可分析400-4000张图）
- **$10+预算**: GPT-4V（最佳效果）

## 🔧 高级功能

### 自定义分析提示词
```python
# 针对特定类型的截图自定义提示
custom_prompt = "这张截图显示的是什么软件？用户正在进行什么操作？有哪些可见的UI元素？"

analyzer.analyze_with_gpt4v(image_path, custom_prompt)
```

### 批量分析配置
```python
# 在 screenshot_analyzer.py 中的 AnalysisConfig 类
class AnalysisConfig:
    MODEL_TYPE = "local"  # "local", "gpt4v", "gemini"
    BATCH_SIZE = 50
    MAX_COST_USD = 10.0  # 成本控制
```

## 🚨 注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥
2. **成本控制**: 设置MAX_COST_USD限制防止意外超支
3. **本地模型**: 首次运行会下载大模型文件
4. **网络连接**: 云端API需要稳定的网络连接

## 📈 性能优化

### 提高分析速度
1. 使用GPU加速（CUDA）
2. 批量处理而非逐张分析
3. 选择轻量级模型（BLIP-2）

### 降低成本
1. 先用免费模型筛选重要截图
2. 只对关键截图使用付费API
3. 压缩图片尺寸降低API成本

## 🆘 故障排除

### 常见问题

**Q: Ollama安装失败**
A: 确保从官网下载，Windows用户注意权限问题

**Q: 显存不足**
A: 尝试BLIP-2或云端API方案

**Q: API调用失败**
A: 检查网络连接和API密钥有效性

**Q: 分析结果不准确**
A: 尝试调整提示词或使用更高质量的模型

## 📞 获取帮助

1. 运行 `python analysis/cost_calculator.py` 获取方案建议
2. 运行 `python analysis/local_analyzer.py` 测试本地模型
3. 查看代码注释了解详细用法

## 🔄 更新日志

- v1.0: 支持多种分析方案
- 添加了成本计算器
- 支持批量分析
- 提供详细的设置指南 