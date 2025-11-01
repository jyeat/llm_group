#!/usr/bin/env python3
"""
回测结果分析脚本

分析回测结果，生成统计报告和可视化图表
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import argparse


def load_backtest_results(summary_file: str):
    """加载回测结果"""
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_backtest_performance(results: list):
    """分析回测表现"""
    
    analysis = {}
    
    for ticker_data in results:
        ticker = ticker_data['ticker']
        ticker_results = ticker_data['results']
        
        if not ticker_results:
            continue
        
        # 统计决策分布
        decisions = [r['decision'] for r in ticker_results]
        bullish_count = decisions.count('bullish')
        bearish_count = decisions.count('bearish')
        neutral_count = decisions.count('neutral')
        total_count = len(decisions)
        
        # 计算平均置信度
        avg_confidence = sum(r['confidence'] for r in ticker_results) / total_count
        
        # 决策变化趋势
        decision_changes = 0
        for i in range(1, len(decisions)):
            if decisions[i] != decisions[i-1]:
                decision_changes += 1
        
        analysis[ticker] = {
            'total_analyses': total_count,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'bullish_ratio': bullish_count / total_count,
            'bearish_ratio': bearish_count / total_count,
            'neutral_ratio': neutral_count / total_count,
            'avg_confidence': avg_confidence,
            'decision_changes': decision_changes,
            'decision_consistency': 1 - (decision_changes / max(1, total_count - 1)),
            'results': ticker_results
        }
    
    return analysis


def generate_summary_report(analysis: dict):
    """生成汇总报告"""
    
    print("=" * 80)
    print("回测分析报告")
    print("=" * 80)
    
    for ticker, data in analysis.items():
        print(f"\n📊 {ticker} 分析结果:")
        print(f"  总分析次数: {data['total_analyses']}")
        print(f"  看涨比例: {data['bullish_ratio']:.1%}")
        print(f"  看跌比例: {data['bearish_ratio']:.1%}")
        print(f"  中性比例: {data['neutral_ratio']:.1%}")
        print(f"  平均置信度: {data['avg_confidence']:.1%}")
        print(f"  决策一致性: {data['decision_consistency']:.1%}")
        print(f"  决策变化次数: {data['decision_changes']}")
        
        # 详细决策历史
        print(f"\n  决策历史:")
        for result in data['results']:
            print(f"    {result['date']}: {result['decision'].upper()} (置信度: {result['confidence']:.1%})")


def create_visualization(analysis: dict, output_dir: str = "backtest_charts"):
    """创建可视化图表"""
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    for ticker, data in analysis.items():
        if not data['results']:
            continue
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{ticker} 回测分析结果', fontsize=16, fontweight='bold')
        
        # 1. 决策分布饼图
        decisions = [r['decision'] for r in data['results']]
        decision_counts = pd.Series(decisions).value_counts()
        
        axes[0, 0].pie(decision_counts.values, labels=decision_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('决策分布')
        
        # 2. 置信度趋势
        dates = [datetime.strptime(r['date'], '%Y-%m-%d') for r in data['results']]
        confidences = [r['confidence'] for r in data['results']]
        
        axes[0, 1].plot(dates, confidences, marker='o', linewidth=2, markersize=6)
        axes[0, 1].set_title('置信度趋势')
        axes[0, 1].set_ylabel('置信度')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. 决策时间线
        decision_map = {'bullish': 1, 'neutral': 0, 'bearish': -1}
        decision_values = [decision_map[d] for d in decisions]
        
        axes[1, 0].plot(dates, decision_values, marker='o', linewidth=2, markersize=8)
        axes[1, 0].set_title('决策时间线')
        axes[1, 0].set_ylabel('决策 (1=看涨, 0=中性, -1=看跌)')
        axes[1, 0].set_ylim(-1.5, 1.5)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 统计摘要
        axes[1, 1].axis('off')
        summary_text = f"""
        总分析次数: {data['total_analyses']}
        看涨比例: {data['bullish_ratio']:.1%}
        看跌比例: {data['bearish_ratio']:.1%}
        中性比例: {data['neutral_ratio']:.1%}
        平均置信度: {data['avg_confidence']:.1%}
        决策一致性: {data['decision_consistency']:.1%}
        决策变化次数: {data['decision_changes']}
        """
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        axes[1, 1].set_title('统计摘要')
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = f"{output_dir}/{ticker}_backtest_analysis.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"📊 {ticker} 图表保存到: {chart_file}")
        
        plt.close()


def export_detailed_results(analysis: dict, output_file: str):
    """导出详细结果到CSV"""
    
    all_results = []
    
    for ticker, data in analysis.items():
        for result in data['results']:
            all_results.append({
                'ticker': ticker,
                'date': result['date'],
                'decision': result['decision'],
                'confidence': result['confidence'],
                'rationale': result['rationale']
            })
    
    df = pd.DataFrame(all_results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"📄 详细结果导出到: {output_file}")


def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(description="回测结果分析工具")
    parser.add_argument("--summary-file", type=str, required=True, help="回测汇总文件路径")
    parser.add_argument("--output-dir", type=str, default="backtest_charts", help="图表输出目录")
    parser.add_argument("--export-csv", type=str, help="导出CSV文件路径")
    parser.add_argument("--no-charts", action="store_true", help="不生成图表")
    
    args = parser.parse_args()
    
    # 加载回测结果
    print("📊 加载回测结果...")
    results = load_backtest_results(args.summary_file)
    
    # 分析回测表现
    print("🔍 分析回测表现...")
    analysis = analyze_backtest_performance(results)
    
    # 生成汇总报告
    print("📋 生成汇总报告...")
    generate_summary_report(analysis)
    
    # 创建可视化图表
    if not args.no_charts:
        print("📊 创建可视化图表...")
        create_visualization(analysis, args.output_dir)
    
    # 导出详细结果
    if args.export_csv:
        print("📄 导出详细结果...")
        export_detailed_results(analysis, args.export_csv)
    
    print("\n✅ 回测分析完成！")


if __name__ == "__main__":
    main()

