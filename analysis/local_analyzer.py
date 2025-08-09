"""
本地免费图像分析方案
支持多种开源模型：LLaVA, BLIP-2, InstructBLIP
"""

import os
import cv2
import torch
from PIL import Image
import subprocess
import json
from typing import List, Dict

class LocalAnalyzer:
    """本地免费图像分析器"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {self.device}")
    
    def setup_ollama_llava(self):
        """设置Ollama + LLaVA（推荐方案）"""
        print("=== 设置Ollama + LLaVA ===")
        print("1. 访问 https://ollama.ai/ 下载并安装Ollama")
        print("2. 在终端运行以下命令：")
        print("   ollama pull llava:7b")
        print("   ollama pull llava:13b  # 如果显存充足（16GB+）")
        print("")
        print("安装完成后，可以使用 test_ollama_llava() 方法测试")
    
    def test_ollama_llava(self, image_path: str) -> str:
        """测试Ollama LLaVA是否正常工作"""
        try:
            cmd = [
                "ollama", "run", "llava:7b",
                f"请用中文详细描述这张屏幕截图显示的内容，包括正在进行的操作： {image_path}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"错误: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "错误: 分析超时"
        except FileNotFoundError:
            return "错误: Ollama未安装，请先安装Ollama"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def setup_blip2(self):
        """设置BLIP-2（轻量级方案）"""
        print("=== 设置BLIP-2 ===")
        print("运行以下命令安装依赖：")
        print("pip install transformers torch torchvision Pillow")
        print("")
        print("BLIP-2模型会在首次使用时自动下载")
    
    def analyze_with_blip2(self, image_path: str) -> str:
        """使用BLIP-2分析图像"""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            # 加载模型（首次运行会下载）
            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # 处理图像
            image = Image.open(image_path).convert('RGB')
            inputs = processor(image, return_tensors="pt")
            
            # 生成描述
            out = model.generate(**inputs, max_length=100)
            caption = processor.decode(out[0], skip_special_tokens=True)
            
            return f"图像描述: {caption}"
            
        except ImportError:
            return "错误: 请安装transformers库 (pip install transformers torch torchvision)"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def setup_instructblip(self):
        """设置InstructBLIP（可回答问题的版本）"""
        print("=== 设置InstructBLIP ===")
        print("pip install transformers torch torchvision Pillow")
        print("")
        print("可以对图像提出具体问题，如：")
        print("- '这个屏幕显示的是什么软件？'")
        print("- '用户正在做什么操作？'")
        print("- '屏幕上有哪些按钮或选项？'")
    
    def analyze_with_instructblip(self, image_path: str, question: str = "这张屏幕截图显示了什么？") -> str:
        """使用InstructBLIP回答关于图像的问题"""
        try:
            from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
            
            model = InstructBlipForConditionalGeneration.from_pretrained("Salesforce/instructblip-vicuna-7b")
            processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")
            
            image = Image.open(image_path).convert('RGB')
            inputs = processor(images=image, text=question, return_tensors="pt")
            
            outputs = model.generate(
                **inputs,
                do_sample=False,
                num_beams=5,
                max_length=256,
                min_length=1,
                top_p=0.9,
                repetition_penalty=1.5,
                length_penalty=1.0,
                temperature=1,
            )
            
            generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
            return generated_text
            
        except ImportError:
            return "错误: 请安装transformers库"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def batch_analyze_local(self, images_dir: str, method: str = "ollama") -> List[Dict]:
        """批量分析图像"""
        results = []
        image_files = [f for f in os.listdir(images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        print(f"使用{method}方法分析 {len(image_files)} 张图片...")
        
        for i, filename in enumerate(image_files):
            image_path = os.path.join(images_dir, filename)
            print(f"正在分析 ({i+1}/{len(image_files)}): {filename}")
            
            if method == "ollama":
                analysis = self.test_ollama_llava(image_path)
            elif method == "blip2":
                analysis = self.analyze_with_blip2(image_path)
            elif method == "instructblip":
                analysis = self.analyze_with_instructblip(image_path)
            else:
                analysis = "错误: 未知的分析方法"
            
            results.append({
                "filename": filename,
                "analysis": analysis,
                "method": method
            })
        
        return results

# 快速开始指南
def quick_start_guide():
    """快速开始指南"""
    print("""
=== 屏幕截图分析 - 免费本地方案快速指南 ===

方案1: Ollama + LLaVA (推荐 - 效果最好)
--------------------------------------
优点: 效果接近GPT-4V，完全免费，支持中文
缺点: 需要显卡，模型较大(4GB)
成本: 完全免费
安装:
  1. 下载安装 Ollama: https://ollama.ai/
  2. 运行: ollama pull llava:7b
  3. 使用: analyzer.test_ollama_llava(image_path)

方案2: BLIP-2 (轻量级)
----------------------
优点: 模型小，普通电脑可运行，快速
缺点: 只能生成简单描述，不支持对话
成本: 完全免费
安装: pip install transformers torch torchvision
使用: analyzer.analyze_with_blip2(image_path)

方案3: InstructBLIP (可问答)
---------------------------
优点: 可以回答具体问题，理解能力较强
缺点: 模型较大，需要较好的显卡
成本: 完全免费
安装: pip install transformers torch torchvision
使用: analyzer.analyze_with_instructblip(image_path, question)

推荐流程:
1. 先试BLIP-2看能否满足需求
2. 如果需要更详细分析，使用Ollama+LLaVA
3. 如果有特定问题要问，使用InstructBLIP
""")

if __name__ == "__main__":
    quick_start_guide()
    
    # 示例使用
    analyzer = LocalAnalyzer()
    
    # 根据你的需求选择设置方法
    print("\n选择要设置的方案:")
    print("1. Ollama + LLaVA (推荐)")
    print("2. BLIP-2 (轻量级)")
    print("3. InstructBLIP (可问答)")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        analyzer.setup_ollama_llava()
    elif choice == "2":
        analyzer.setup_blip2()
    elif choice == "3":
        analyzer.setup_instructblip()
    else:
        print("无效选择") 