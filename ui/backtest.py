#!/usr/bin/env python3
"""
股票分析回测脚本

支持批量分析不同日期的股票，用于回测验证
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from trading_graph import create_trading_graph


def get_historical_dates(start_date: str, end_date: str, interval_days: int = 30):
    """
    生成历史日期列表
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        interval_days: 间隔天数
    
    Returns:
        日期字符串列表
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates = []
    current = start
    
    while current <= end:
        # 只包含工作日（周一到周五）
        if current.weekday() < 5:
            dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=interval_days)
    
    return dates


def analyze_stock(ticker: str, date: str, debug: bool = False):
    """
    分析单个股票
    
    Args:
        ticker: 股票代码
        date: 分析日期
        debug: 是否启用调试模式
    
    Returns:
        分析结果字典
    """
    try:
        print(f"\n{'='*60}")
        print(f"分析 {ticker} - {date}")
        print(f"{'='*60}")
        
        # 创建图
        graph = create_trading_graph(debug=debug)
        
        # 运行分析
        result = graph.analyze(ticker=ticker, date=date)
        
        # 保存结果
        output_file = f"analysis_{ticker}_{date}.json"
        result_to_save = {k: v for k, v in result.items() if k != 'messages'}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 分析完成，结果保存到: {output_file}")
        print(f"决策: {result.get('decision', 'N/A').upper()}")
        print(f"置信度: {result.get('confidence', 0.0):.2%}")
        
        return result
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None


def batch_analyze(tickers: list, start_date: str, end_date: str, interval_days: int = 30, debug: bool = False):
    """
    批量分析多个股票
    
    Args:
        tickers: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        interval_days: 间隔天数
        debug: 是否启用调试模式
    """
    print(f"开始批量回测分析")
    print(f"股票: {', '.join(tickers)}")
    print(f"日期范围: {start_date} 到 {end_date}")
    print(f"间隔: {interval_days}天")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    
    # 生成日期列表
    dates = get_historical_dates(start_date, end_date, interval_days)
    print(f"将分析 {len(dates)} 个日期: {dates}")
    
    # 存储所有结果
    all_results = []
    
    for ticker in tickers:
        print(f"\n{'='*80}")
        print(f"开始分析股票: {ticker}")
        print(f"{'='*80}")
        
        ticker_results = []
        
        for date in dates:
            result = analyze_stock(ticker, date, debug)
            if result:
                ticker_results.append({
                    'date': date,
                    'ticker': ticker,
                    'decision': result.get('decision', 'N/A'),
                    'confidence': result.get('confidence', 0.0),
                    'rationale': result.get('rationale', 'N/A')
                })
        
        all_results.append({
            'ticker': ticker,
            'results': ticker_results
        })
    
    # 保存汇总结果
    summary_file = f"backtest_summary_{start_date}_to_{end_date}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"批量分析完成！")
    print(f"汇总结果保存到: {summary_file}")
    print(f"{'='*80}")
    
    # 打印简要统计
    for ticker_data in all_results:
        ticker = ticker_data['ticker']
        results = ticker_data['results']
        
        if results:
            decisions = [r['decision'] for r in results]
            bullish_count = decisions.count('bullish')
            bearish_count = decisions.count('bearish')
            neutral_count = decisions.count('neutral')
            
            print(f"\n{ticker} 分析结果:")
            print(f"  看涨: {bullish_count} 次")
            print(f"  看跌: {bearish_count} 次")
            print(f"  中性: {neutral_count} 次")
            print(f"  总计: {len(results)} 次分析")


def main():
    """主函数"""
    
    parser = argparse.ArgumentParser(description="股票分析回测工具")
    parser.add_argument("--ticker", type=str, help="股票代码 (单个)")
    parser.add_argument("--tickers", type=str, nargs='+', help="股票代码列表 (多个)")
    parser.add_argument("--date", type=str, help="分析日期 (YYYY-MM-DD)")
    parser.add_argument("--start-date", type=str, help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--interval", type=int, default=30, help="间隔天数 (默认30天)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 单股票单日期分析
    if args.ticker and args.date:
        analyze_stock(args.ticker, args.date, args.debug)
    
    # 批量分析
    elif args.tickers and args.start_date and args.end_date:
        batch_analyze(args.tickers, args.start_date, args.end_date, args.interval, args.debug)
    
    # 单股票多日期分析
    elif args.ticker and args.start_date and args.end_date:
        batch_analyze([args.ticker], args.start_date, args.end_date, args.interval, args.debug)
    
    else:
        print("使用方法:")
        print("1. 单股票单日期: python backtest.py --ticker AAPL --date 2024-06-15")
        print("2. 单股票多日期: python backtest.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-06-30")
        print("3. 多股票多日期: python backtest.py --tickers AAPL MSFT GOOGL --start-date 2024-01-01 --end-date 2024-06-30")
        print("4. 启用调试: 添加 --debug 参数")


if __name__ == "__main__":
    main()

