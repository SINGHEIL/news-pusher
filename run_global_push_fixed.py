#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版全球新闻推送 - 精简内容避免微信限制
"""

import sys
import logging
import os
from datetime import datetime

# ========== 修复导入路径 ==========
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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

class SimpleReportGenerator:
    """简单报告生成器，确保不超过600字符"""
    
    @staticmethod
    def shorten_text(text, max_len):
        """缩短文本"""
        if len(text) <= max_len:
            return text
        return text[:max_len-3] + "..."
    
    def generate_report(self, cn_news, int_news, cn_count, int_count):
        """生成精简报告"""
        total = cn_count + int_count
        
        # 基础信息
        report = "🌍 全球新闻简报\n"
        report += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        report += f"📊 统计: 国内{cn_count}条 + 国际{int_count}条 = {total}条\n\n"
        
        # 精选重要新闻
        important_news = []
        
        # 从国内新闻选最重要的
        for category, news_list in cn_news.items():
            if news_list:
                # 取最新的一条
                news = news_list[0]
                title = self.shorten_text(news['title'], 35)
                important_news.append(f"🇨🇳 {title}")
        
        # 从国际新闻选最重要的
        for category, news_list in int_news.items():
            if news_list:
                # 取最新的一条
                news = news_list[0]
                title = self.shorten_text(news['title'], 35)
                important_news.append(f"🌐 {title}")
        
        # 只显示最重要的5条
        if important_news:
            report += "📰 今日要闻:\n"
            for i, item in enumerate(important_news[:5], 1):
                report += f"{i}. {item}\n"
        
        # 确保不超过600字符
        if len(report) > 550:  # 留50字符余地
            report = report[:520] + "...\n[内容已精简]"
        
        return report

def main():
    """主函数：精简版推送"""
    try:
        logger.info("=" * 60)
        logger.info("开始精简版全球新闻推送")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # 1. 导入模块
        logger.info("加载模块...")
        try:
            from enhanced_news_fetcher import EnhancedNewsFetcher
            from international_news_fetcher import InternationalNewsFetcher
            from wechat_notifier import WeChatNotifier
        except ImportError as e:
            logger.error(f"模块导入失败: {str(e)}")
            sys.exit(1)
        
        logger.info("✅ 模块加载成功")
        
        # 2. 抓取国内新闻（精简版）
        logger.info("抓取国内新闻...")
        cn_fetcher = EnhancedNewsFetcher()
        cn_news = cn_fetcher.fetch_all_news()
        cn_count = sum(len(news_list) for news_list in cn_news.values())
        
        # 精简国内新闻数量（每个分类最多2条）
        filtered_cn_news = {}
        for category, news_list in cn_news.items():
            filtered_cn_news[category] = news_list[:2]
        
        logger.info(f"✅ 国内新闻抓取完成: {cn_count}条，精简后{sum(len(v) for v in filtered_cn_news.values())}条")
        
        # 3. 抓取国际新闻（精简版）
        logger.info("抓取外网新闻...")
        int_fetcher = InternationalNewsFetcher()
        int_news = int_fetcher.fetch_all_international_news()
        int_count = sum(len(news_list) for news_list in int_news.values())
        
        # 精简国际新闻数量
        filtered_int_news = {}
        for category, news_list in int_news.items():
            filtered_int_news[category] = news_list[:2]
        
        logger.info(f"✅ 国际新闻抓取完成: {int_count}条，精简后{sum(len(v) for v in filtered_int_news.values())}条")
        
        # 4. 生成精简报告
        logger.info("生成精简报告...")
        generator = SimpleReportGenerator()
        report = generator.generate_report(filtered_cn_news, filtered_int_news, cn_count, int_count)
        
        logger.info(f"报告长度: {len(report)}字符")
        logger.info("报告预览:\n" + "-" * 40)
        logger.info(report[:200] + "..." if len(report) > 200 else report)
        logger.info("-" * 40)
        
        # 5. 微信推送（精简版）
        logger.info("微信推送...")
        notifier_config = {
            'WECHAT_TEST': True,
            'WECHAT_TEST_APPID': os.getenv('WECHAT_TEST_APPID', ''),
            'WECHAT_TEST_SECRET': os.getenv('WECHAT_TEST_SECRET', ''),
            'WECHAT_TEST_TOUSER': os.getenv('WECHAT_TEST_TOUSER', ''),
        }
        
        notifier = WeChatNotifier(notifier_config)
        
        # 直接发送，不分割（因为我们已经确保<600字符）
        success = notifier.send_message(report)
        
        if success:
            logger.info("✅ 推送成功！")
            
            # 记录统计
            stats_content = f"""# 新闻推送统计
推送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 抓取统计
- 国内新闻: {cn_count} 条
- 国际新闻: {int_count} 条  
- 总计: {cn_count + int_count} 条

## 推送状态
- 状态: 成功
- 时间: {datetime.now().strftime('%H:%M:%S')}
- 内容长度: {len(report)} 字符
"""
            with open("news_statistics.md", "w", encoding="utf-8") as f:
                f.write(stats_content)
            
        else:
            logger.error("❌ 推送失败")
            logger.info("可能是微信测试号每日限制已达上限")
            logger.info("建议: 1) 等待24小时重置 2) 注册正式公众号")
            
    except Exception as e:
        logger.error(f"❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()