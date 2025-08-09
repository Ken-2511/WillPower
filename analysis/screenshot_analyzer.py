import os
import cv2
import base64
import requests
from typing import List, Dict, Optional
import json
from datetime import datetime

class ScreenshotAnalyzer:
    """屏幕截图内容分析器 - 支持多种AI模型"""
    
    def __init__(self, api_key: str = None, model_type: str = "local"):
        self.api_key = api_key
        self.model_type = model_type
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64格式"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_with_gpt4v(self, image_path: str, prompt: str = "这张屏幕截图显示了什么内容？正在进行什么操作？") -> str:
        """使用GPT-4V分析截图"""
        if not self.api_key:
            return "错误：需要OpenAI API密钥"
            
        base64_image = self.encode_image_to_base64(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=payload)
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def analyze_with_gemini(self, image_path: str, prompt: str = "描述这张屏幕截图的内容和正在进行的操作") -> str:
        """使用Google Gemini分析截图"""
        # 这里需要Google AI API密钥
        # 实现类似GPT-4V的调用逻辑
        return "Gemini分析功能待实现"
    
    def analyze_with_local_model(self, image_path: str) -> str:
        """使用本地模型分析截图（如LLaVA）"""
        try:
            # 这里可以集成ollama + llava
            # 或者其他本地部署的多模态模型
            import subprocess
            
            # 示例：使用ollama调用llava
            result = subprocess.run([
                "ollama", "run", "llava:7b", 
                f"请描述这张屏幕截图显示的内容：{image_path}"
            ], capture_output=True, text=True)
            
            return result.stdout if result.returncode == 0 else "本地模型分析失败"
        except:
            return "本地模型未安装或配置错误"
    
    def batch_analyze_screenshots(self, screenshots_dir: str, output_file: str = None) -> List[Dict]:
        """批量分析截图"""
        results = []
        
        # 获取所有截图文件
        image_files = [f for f in os.listdir(screenshots_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        print(f"找到 {len(image_files)} 张截图，开始分析...")
        
        for i, filename in enumerate(image_files):
            image_path = os.path.join(screenshots_dir, filename)
            print(f"正在分析 ({i+1}/{len(image_files)}): {filename}")
            
            # 根据配置选择分析方法
            if self.model_type == "gpt4v":
                analysis = self.analyze_with_gpt4v(image_path)
            elif self.model_type == "gemini":
                analysis = self.analyze_with_gemini(image_path)
            else:
                analysis = self.analyze_with_local_model(image_path)
            
            result = {
                "filename": filename,
                "timestamp": filename.split("_____")[0] if "_____" in filename else filename.split(".")[0],
                "analysis": analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # 实时保存进度（防止中断丢失）
            if output_file and i % 10 == 0:
                self.save_results(results, output_file)
        
        # 保存最终结果
        if output_file:
            self.save_results(results, output_file)
            
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        """保存分析结果到JSON文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def generate_summary_report(self, results: List[Dict]) -> str:
        """生成分析摘要报告"""
        total_images = len(results)
        successful_analyses = len([r for r in results if not r['analysis'].startswith('错误') and not r['analysis'].startswith('分析失败')])
        
        report = f"""
=== 屏幕截图分析报告 ===
总截图数量: {total_images}
成功分析: {successful_analyses}
分析成功率: {successful_analyses/total_images*100:.1f}%

=== 时间分布 ===
"""
        
        # 按小时统计活动
        hour_activity = {}
        for result in results:
            try:
                timestamp = result['timestamp']
                hour = timestamp.split('-')[0]  # 假设格式为 HH-MM-SS
                hour_activity[hour] = hour_activity.get(hour, 0) + 1
            except:
                continue
        
        for hour in sorted(hour_activity.keys()):
            report += f"{hour}:00 - {hour_activity[hour]} 张截图\n"
        
        return report


# 使用示例和配置
class AnalysisConfig:
    """分析配置类"""
    
    # API密钥配置
    OPENAI_API_KEY = ""  # 填入你的OpenAI API密钥
    GOOGLE_API_KEY = ""  # 填入你的Google API密钥
    
    # 模型选择: "local", "gpt4v", "gemini"
    MODEL_TYPE = "local"
    
    # 批量处理配置
    BATCH_SIZE = 50  # 每批处理的图片数量
    
    # 成本控制
    MAX_COST_USD = 10.0  # 最大花费限制（美元）


if __name__ == "__main__":
    # 使用示例
    from datetime import datetime
    
    # Configuration
    SCREENSHOTS_PATH = r"D:\screenCap"
    DATE = str(datetime.now().date())
    OUTPUT_PATH = r"C:\Users\IWMAI\Desktop"
    
    # 初始化分析器
    analyzer = ScreenshotAnalyzer(
        api_key=AnalysisConfig.OPENAI_API_KEY,
        model_type=AnalysisConfig.MODEL_TYPE
    )
    
    # 设置截图目录
    screenshots_dir = os.path.join(SCREENSHOTS_PATH, DATE)
    output_file = os.path.join(OUTPUT_PATH, f"screenshot_analysis_{DATE}.json")
    
    print("开始批量分析屏幕截图...")
    
    # 执行批量分析
    results = analyzer.batch_analyze_screenshots(screenshots_dir, output_file)
    
    # 生成报告
    report = analyzer.generate_summary_report(results)
    print(report)
    
    # 保存报告
    report_file = os.path.join(OUTPUT_PATH, f"analysis_report_{DATE}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"分析完成！结果保存到: {output_file}")
    print(f"报告保存到: {report_file}") 