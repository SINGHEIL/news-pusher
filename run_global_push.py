#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全球新闻推送系统
整合国内新闻和外网一线消息
"""

import sys
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('global_news_push.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数：整合国内和国际新闻推送"""
    try:
        logger.info("=" * 60)
        logger.info("开始全球新闻推送任务")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 1. 导入模块
        logger.info("加载模块...")
        try:
            from enhanced_news_fetcher import EnhancedNewsFetcher
            from international_news_fetcher import InternationalNewsFetcher
            from enhanced_report_generator import EnhancedReportGenerator
            from wechat_notifier import WeChatNotifier
        except ImportError as e:
            logger.error(f"模块导入失败: {str(e)}")
            logger.info("请确保已安装所有依赖: pip install -r requirements.txt")
            sys.exit(1)
        
        # 2. 抓取国内新闻
        logger.info("开始抓取国内新闻...")
        cn_fetcher = EnhancedNewsFetcher()
        cn_news = cn_fetcher.fetch_all_news()
        
        cn_count = sum(len(news_list) for news_list in cn_news.values())
        logger.info(f"国内新闻抓取完成，共 {cn_count} 条")
        
        # 3. 抓取国际新闻
        logger.info("开始抓取外网一线消息...")
        int_fetcher = InternationalNewsFetcher()
        int_news = int_fetcher.fetch_all_international_news()
        
        int_count = sum(len(news_list) for news_list in int_news.values())
        logger.info(f"国际新闻抓取完成，共 {int_count} 条")
        
        # 4. 合并新闻数据
        logger.info("合并新闻数据...")
        all_news = {}
        
        # 国内新闻分类
        for category, news_list in cn_news.items():
            if news_list:
                all_news[f"国内-{category}"] = news_list
        
        # 国际新闻分类
        for category, news_list in int_news.items():
            if news_list:
                all_news[f"国际-{category}"] = news_list
        
        # 5. 生成简报
        logger.info("生成全球新闻简报...")
        generator = EnhancedReportGenerator()
        
        # 创建专门的全球新闻格式
        global_report = generate_global_report(all_news, cn_count, int_count)
        
        # 6. 推送微信
        logger.info("初始化微信推送...")
        notifier_config = {
            'WECHAT_TEST': True,
            'WECHAT_TEST_APPID': os.getenv('WECHAT_TEST_APPID', ''),
            'WECHAT_TEST_SECRET': os.getenv('WECHAT_TEST_SECRET', ''),
            'WECHAT_TEST_TOUSER': os.getenv('WECHAT_TEST_TOUSER', ''),
        }
        
        notifier = WeChatNotifier(notifier_config)
        
        # 7. 发送推送
        logger.info("推送到微信...")
        success = notifier.format_and_send(global_report)
        
        if success:
            logger.info("✅ 全球新闻推送成功!")
            
            # 生成统计报告
            generate_statistics_report(cn_news, int_news)
        else:
            logger.error("❌ 推送失败!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)
        sys.exit(1)

def generate_global_report(all_news: dict, cn_count: int, int_count: int) -> str:
    """生成全球新闻简报"""
    report_lines = []
    
    # 标题
    report_lines.append("🌍 全球新闻速递")
    report_lines.append(f"📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    report_lines.append("=" * 40)
    
    # 统计信息
    report_lines.append(f"📊 今日新闻统计:")
    report_lines.append(f"  国内新闻: {cn_count} 条")
    report_lines.append(f"  国际新闻: {int_count} 条")
    report_lines.append(f"  总计: {cn_count + int_count} 条")
    report_lines.append("")
    
    # 国内新闻部分
    report_lines.append("🇨🇳 国内要闻")
    report_lines.append("-" * 30)
    
    cn_categories = [cat for cat in all_news.keys() if cat.startswith('国内-')]
    for category in cn_categories:
        news_list = all_news[category]
        if news_list:
            # 简化分类名
            simple_cat = category.replace('国内-', '')
            report_lines.append(f"【{simple_cat}】")
            
            for i, news in enumerate(news_list[:2], 1):  # 每个分类最多2条
                title = news['title'][:40] + '...' if len(news['title']) > 40 else news['title']
                report_lines.append(f"{i}. {title}")
                if 'content' in news and news['content']:
                    content_preview = news['content'][:60] + '...' if len(news['content']) > 60 else news['content']
                    report_lines.append(f"   📝 {content_preview}")
            report_lines.append("")
    
    # 国际新闻部分
    report_lines.append("🌐 国际动态")
    report_lines.append("-" * 30)
    
    int_categories = [cat for cat in all_news.keys() if cat.startswith('国际-')]
    for category in int_categories:
        news_list = all_news[category]
        if news_list:
            # 简化分类名
            simple_cat = category.replace('国际-', '')
            report_lines.append(f"【{simple_cat}】")
            
            for i, news in enumerate(news_list[:2], 1):  # 每个分类最多2条
                title = news['title'][:40] + '...' if len(news['title']) > 40 else news['title']
                report_lines.append(f"{i}. {title}")
                if 'content' in news and news['content']:
                    content_preview = news['content'][:60] + '...' if len(news['content']) > 60 else news['content']
                    report_lines.append(f"   📝 {content_preview}")
            report_lines.append("")
    
    # 金融数据部分
    report_lines.append("💰 金融市场")
    report_lines.append("-" * 30)
    
    financial_categories = ['国际-金融数据', '国际-加密货币']
    for category in financial_categories:
        if category in all_news and all_news[category]:
            for news in all_news[category]:
                if 'content' in news:
                    report_lines.append(news['content'])
                    report_lines.append("")
    
    # 结尾
    report_lines.append("=" * 40)
    report_lines.append("📱 更多详细新闻请点击链接查看")
    report_lines.append("⏰ 下次推送时间: 明天 09:00")
    
    return "\n".join(report_lines)

def generate_statistics_report(cn_news: dict, int_news: dict):
    """生成统计报告文件"""
    try:
        stats_file = "news_statistics.md"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(f"# 新闻推送统计报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 国内新闻统计\n")
            f.write("| 分类 | 数量 |\n")
            f.write("|------|------|\n")
            for category, news_list in cn_news.items():
                if news_list:
                    f.write(f"| {category} | {len(news_list)} |\n")
            
            f.write("\n## 国际新闻统计\n")
            f.write("| 分类 | 数量 |\n")
            f.write("|------|------|\n")
            for category, news_list in int_news.items():
                if news_list:
                    f.write(f"| {category} | {len(news_list)} |\n")
            
            total_cn = sum(len(news_list) for news_list in cn_news.values())
            total_int = sum(len(news_list) for news_list in int_news.values())
            
            f.write(f"\n## 总计\n")
            f.write(f"- 国内新闻: {total_cn} 条\n")
            f.write(f"- 国际新闻: {total_int} 条\n")
            f.write(f"- 总计: {total_cn + total_int} 条\n")
        
        logger.info(f"统计报告已保存到: {stats_file}")
    except Exception as e:
        logger.error(f"生成统计报告失败: {str(e)}")

def test_international_fetcher():
    """测试国际新闻抓取器"""
    logger.info("测试国际新闻抓取器...")
    try:
        from international_news_fetcher import InternationalNewsFetcher
        
        fetcher = InternationalNewsFetcher()
        top_news = fetcher.get_top_international_news(limit_per_category=1)
        
        logger.info(f"测试抓取到 {len(top_news)} 条国际新闻")
        
        for news in top_news[:3]:  # 显示前3条
            logger.info(f"[{news['category']}] {news['source']}: {news['title'][:60]}...")
        
        return len(top_news) > 0
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 检查是否要运行测试
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        if test_international_fetcher():
            logger.info("✅ 国际新闻抓取测试通过")
        else:
            logger.error("❌ 国际新闻抓取测试失败")
    else:
        main()