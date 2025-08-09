"""
屏幕截图分析成本计算器
帮助用户选择最经济的分析方案
"""

from dataclasses import dataclass
from typing import List, Dict
import math

@dataclass
class AnalysisOption:
    """分析方案选项"""
    name: str
    cost_per_image: float  # 美元/张
    setup_cost: float      # 一次性设置成本
    quality_score: int     # 质量评分 1-10
    speed_score: int       # 速度评分 1-10
    setup_difficulty: str  # "简单", "中等", "困难"
    requirements: List[str]  # 硬件/软件要求
    pros: List[str]        # 优点
    cons: List[str]        # 缺点

class CostCalculator:
    """成本计算器"""
    
    def __init__(self):
        self.options = self._initialize_options()
    
    def _initialize_options(self) -> List[AnalysisOption]:
        """初始化所有分析方案"""
        return [
            AnalysisOption(
                name="Ollama + LLaVA 7B",
                cost_per_image=0.0,
                setup_cost=0.0,
                quality_score=8,
                speed_score=6,
                setup_difficulty="简单",
                requirements=["显卡（4GB显存）", "网络下载4GB模型"],
                pros=["完全免费", "效果接近GPT-4V", "支持中文", "隐私保护"],
                cons=["需要显卡", "初次设置需下载大模型", "分析速度较慢"]
            ),
            AnalysisOption(
                name="BLIP-2",
                cost_per_image=0.0,
                setup_cost=0.0,
                quality_score=5,
                speed_score=9,
                setup_difficulty="简单",
                requirements=["Python环境", "2GB显存或CPU"],
                pros=["完全免费", "轻量级", "速度快", "CPU可运行"],
                cons=["功能有限", "只能生成简单描述", "不支持中文对话"]
            ),
            AnalysisOption(
                name="GPT-4V",
                cost_per_image=0.01,
                setup_cost=0.0,
                quality_score=10,
                speed_score=8,
                setup_difficulty="简单",
                requirements=["OpenAI API密钥", "网络连接"],
                pros=["效果最佳", "支持中文", "响应快", "无需本地资源"],
                cons=["需要付费", "依赖网络", "隐私风险"]
            ),
            AnalysisOption(
                name="Google Gemini Pro Vision",
                cost_per_image=0.0025,
                setup_cost=0.0,
                quality_score=9,
                speed_score=9,
                setup_difficulty="简单",
                requirements=["Google API密钥", "网络连接"],
                pros=["性价比极高", "速度快", "Google技术", "支持中文"],
                cons=["需要付费", "依赖网络", "API限制"]
            ),
            AnalysisOption(
                name="Claude 3 Haiku Vision",
                cost_per_image=0.004,
                setup_cost=0.0,
                quality_score=8,
                speed_score=10,
                setup_difficulty="简单",
                requirements=["Anthropic API密钥", "网络连接"],
                pros=["响应极快", "理解准确", "API稳定"],
                cons=["需要付费", "相对较贵", "中文支持一般"]
            ),
            AnalysisOption(
                name="InstructBLIP",
                cost_per_image=0.0,
                setup_cost=0.0,
                quality_score=7,
                speed_score=5,
                setup_difficulty="中等",
                requirements=["显卡（8GB显存）", "Python深度学习环境"],
                pros=["完全免费", "可回答具体问题", "理解能力强"],
                cons=["需要大显存", "设置复杂", "分析较慢"]
            )
        ]
    
    def calculate_cost(self, num_images: int, option_name: str) -> Dict:
        """计算特定方案的总成本"""
        option = next((opt for opt in self.options if opt.name == option_name), None)
        if not option:
            return {"error": "未找到指定方案"}
        
        analysis_cost = num_images * option.cost_per_image
        total_cost = option.setup_cost + analysis_cost
        
        return {
            "option": option.name,
            "num_images": num_images,
            "setup_cost": option.setup_cost,
            "analysis_cost": analysis_cost,
            "total_cost": total_cost,
            "cost_per_image": option.cost_per_image
        }
    
    def compare_all_options(self, num_images: int) -> List[Dict]:
        """比较所有方案的成本和效果"""
        results = []
        
        for option in self.options:
            cost_info = self.calculate_cost(num_images, option.name)
            
            results.append({
                **cost_info,
                "quality_score": option.quality_score,
                "speed_score": option.speed_score,
                "setup_difficulty": option.setup_difficulty,
                "total_score": (option.quality_score + option.speed_score) / 2
            })
        
        # 按总成本排序
        results.sort(key=lambda x: x["total_cost"])
        return results
    
    def recommend_best_option(self, num_images: int, budget_usd: float = None, 
                            priority: str = "cost") -> Dict:
        """推荐最佳方案"""
        comparisons = self.compare_all_options(num_images)
        
        if budget_usd:
            # 过滤在预算内的方案
            affordable = [c for c in comparisons if c["total_cost"] <= budget_usd]
            if not affordable:
                return {"error": f"预算${budget_usd}内没有合适的方案"}
            comparisons = affordable
        
        if priority == "cost":
            # 优先考虑成本
            best = min(comparisons, key=lambda x: x["total_cost"])
        elif priority == "quality":
            # 优先考虑质量
            best = max(comparisons, key=lambda x: x["quality_score"])
        elif priority == "speed":
            # 优先考虑速度
            best = max(comparisons, key=lambda x: x["speed_score"])
        else:
            # 综合评分
            best = max(comparisons, key=lambda x: x["total_score"])
        
        return best
    
    def print_detailed_comparison(self, num_images: int):
        """打印详细的方案对比"""
        print(f"\n=== {num_images}张图片的分析方案对比 ===\n")
        
        comparisons = self.compare_all_options(num_images)
        
        for i, comp in enumerate(comparisons, 1):
            option = next(opt for opt in self.options if opt.name == comp["option"])
            
            print(f"{i}. {option.name}")
            print(f"   💰 总成本: ${comp['total_cost']:.4f}")
            print(f"   📊 质量评分: {option.quality_score}/10")
            print(f"   ⚡ 速度评分: {option.speed_score}/10")
            print(f"   🔧 设置难度: {option.setup_difficulty}")
            
            print(f"   ✅ 优点: {', '.join(option.pros)}")
            print(f"   ❌ 缺点: {', '.join(option.cons)}")
            print(f"   📋 要求: {', '.join(option.requirements)}")
            print()
    
    def get_option_details(self, option_name: str) -> AnalysisOption:
        """获取特定方案的详细信息"""
        return next((opt for opt in self.options if opt.name == option_name), None)

def cost_break_points_analysis():
    """成本断点分析 - 在什么数量下哪种方案最经济"""
    calc = CostCalculator()
    
    print("=== 成本断点分析 ===\n")
    
    image_counts = [10, 50, 100, 500, 1000, 5000, 10000]
    
    for count in image_counts:
        print(f"📊 {count}张图片:")
        
        # 找出最便宜的付费和免费方案
        free_options = [opt for opt in calc.options if opt.cost_per_image == 0]
        paid_options = [opt for opt in calc.options if opt.cost_per_image > 0]
        
        if free_options:
            best_free = max(free_options, key=lambda x: x.quality_score)
            print(f"   最佳免费: {best_free.name} (质量: {best_free.quality_score}/10)")
        
        if paid_options:
            best_paid = min(paid_options, key=lambda x: x.cost_per_image)
            cost = count * best_paid.cost_per_image
            print(f"   最便宜付费: {best_paid.name} (${cost:.2f}, 质量: {best_paid.quality_score}/10)")
        
        print()

def interactive_cost_calculator():
    """交互式成本计算器"""
    calc = CostCalculator()
    
    print("=== 屏幕截图分析成本计算器 ===\n")
    
    try:
        num_images = int(input("请输入要分析的截图数量: "))
        
        print(f"\n预算选择:")
        print("1. 完全免费")
        print("2. 低预算 ($1-10)")
        print("3. 中等预算 ($10-50)")
        print("4. 不限预算")
        
        budget_choice = input("请选择预算范围 (1-4): ").strip()
        
        budget_map = {
            "1": 0,
            "2": 10,
            "3": 50,
            "4": float('inf')
        }
        
        budget = budget_map.get(budget_choice, float('inf'))
        
        print(f"\n优先级选择:")
        print("1. 成本优先")
        print("2. 质量优先")
        print("3. 速度优先")
        print("4. 综合平衡")
        
        priority_choice = input("请选择优先级 (1-4): ").strip()
        
        priority_map = {
            "1": "cost",
            "2": "quality", 
            "3": "speed",
            "4": "balanced"
        }
        
        priority = priority_map.get(priority_choice, "balanced")
        
        # 显示详细对比
        calc.print_detailed_comparison(num_images)
        
        # 推荐最佳方案
        if budget == 0:
            # 只考虑免费方案
            free_comparisons = [c for c in calc.compare_all_options(num_images) 
                              if c["total_cost"] == 0]
            if priority == "quality":
                recommended = max(free_comparisons, key=lambda x: x["quality_score"])
            else:
                recommended = max(free_comparisons, key=lambda x: x["total_score"])
        else:
            recommended = calc.recommend_best_option(num_images, budget, priority)
        
        print("🎯 推荐方案:")
        print(f"   方案: {recommended['option']}")
        print(f"   总成本: ${recommended['total_cost']:.4f}")
        print(f"   质量评分: {recommended['quality_score']}/10")
        print(f"   速度评分: {recommended['speed_score']}/10")
        
        # 获取详细信息
        option_details = calc.get_option_details(recommended['option'])
        print(f"\n📋 设置要求:")
        for req in option_details.requirements:
            print(f"   • {req}")
        
        print(f"\n✅ 主要优点:")
        for pro in option_details.pros:
            print(f"   • {pro}")
            
    except ValueError:
        print("输入无效，请输入数字")
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用成本计算器！")

if __name__ == "__main__":
    # 运行断点分析
    cost_break_points_analysis()
    
    # 运行交互式计算器
    interactive_cost_calculator() 