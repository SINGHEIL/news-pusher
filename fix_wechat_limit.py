#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复微信测试号推送限制问题
错误代码: 45047 - out of response count limit
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def analyze_wechat_limit():
    """分析微信测试号限制问题"""
    print("=" * 60)
    print("微信测试号推送限制分析")
    print("=" * 60)
    
    print("\n📊 错误分析:")
    print("错误代码: 45047")
    print("错误信息: 'out of response count limit'")
    print("")
    
    print("🔍 问题原因:")
    print("1. 微信测试号有严格的推送限制:")
    print("   - 每天最多发送100条消息")
    print("   - 每分钟最多发送20条消息")
    print("   - 每次推送内容不能超过600字符")
    print("")
    
    print("📋 您的具体情况:")
    print("1. 内容长度: 3071 字符（太长！）")
    print("2. 分段发送: 5 段")
    print("3. 每段长度: 600-700字符")
    print("4. GitHub Actions可能频繁测试，导致超限")
    print("")
    
    print("🎯 解决方案:")
    
    print("\n方案1: 精简推送内容（推荐）")
    print("修改 run_global_push.py，减少新闻数量:")
    print("""
# 在 run_global_push.py 中修改
def main():
    # ... 抓取新闻后 ...
    
    # 限制新闻数量
    MAX_NEWS_PER_CATEGORY = 3  # 每个分类最多3条
    filtered_news = {}
    
    for category, news_list in all_news.items():
        filtered_news[category] = news_list[:MAX_NEWS_PER_CATEGORY]
    
    # 使用过滤后的新闻生成简报
    global_report = generate_global_report(filtered_news, ...)
""")
    
    print("\n方案2: 优化内容格式")
    print("修改 enhanced_report_generator.py，缩短摘要:")
    print("""
# 在 enhanced_report_generator.py 中修改
def generate_global_report(self, all_news, cn_count, int_count):
    # 缩短标题和摘要
    report = "🌍 全球新闻简报\\n\\n"
    
    for category, news_list in all_news.items():
        if news_list:
            report += f"📰 {category}:\\n"
            for i, news in enumerate(news_list[:3]):  # 只显示前3条
                # 缩短标题
                title = news['title'][:30] + "..." if len(news['title']) > 30 else news['title']
                report += f"{i+1}. {title}\\n"
            report += "\\n"
    
    return report[:600]  # 确保不超过600字符
""")
    
    print("\n方案3: 使用摘要模式")
    print("只推送最重要的新闻摘要:")
    print("""
# 创建摘要模式
def generate_summary_report(all_news):
    '''生成简洁摘要'''
    report = "📰 今日要闻摘要\\n\\n"
    
    # 只选择最重要的新闻
    important_categories = ['国内-政治', '国内-财经', '国际-头条', '国际-财经']
    
    for category in important_categories:
        if category in all_news and all_news[category]:
            news = all_news[category][0]  # 只取第一条
            title = news['title'][:40] + "..." if len(news['title']) > 40 else news['title']
            report += f"• {title}\\n"
    
    report += "\\n📊 统计: 共抓取 {} 条新闻".format(
        sum(len(news_list) for news_list in all_news.values())
    )
    
    return report
""")
    
    print("\n方案4: 调整GitHub Actions频率")
    print("修改 .github/workflows/final-push.yml:")
    print("""
# 减少测试频率
on:
  schedule:
    # 改为每天一次，避免频繁测试
    - cron: '0 1 * * *'  # 北京时间9:00
  # 移除 workflow_dispatch 或谨慎使用
  # workflow_dispatch:
""")
    
    print("\n方案5: 使用正式公众号")
    print("注册正式公众号（无推送限制）:")
    print("1. 访问 https://mp.weixin.qq.com")
    print("2. 注册订阅号（个人）或服务号（企业）")
    print("3. 获取新的AppID和Secret")
    print("4. 更新config.py中的配置")
    
    print("\n🛠️ 立即修复步骤:")
    print("1. 修改 run_global_push.py，添加新闻数量限制")
    print("2. 修改 enhanced_report_generator.py，缩短内容")
    print("3. 重新上传到GitHub")
    print("4. 等待24小时让微信限制重置")
    print("5. 再次测试GitHub Actions")
    
    print("\n📞 验证修复:")
    print("修复后，推送内容应该:")
    print("✅ 总长度 < 600 字符")
    print("✅ 不需要分段发送")
    print("✅ 包含核心新闻摘要")
    
    print("\n" + "=" * 60)
    
    # 创建修复文件
    create_fix_files()

def create_fix_files():
    """创建修复文件"""
    
    # 1. 创建修复版报告生成器
    fix_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版报告生成器 - 精简内容避免微信限制
"""

class FixedReportGenerator:
    def __init__(self):
        pass
    
    def generate_global_report(self, all_news, cn_count, int_count):
        """生成精简版全球新闻简报"""
        
        # 统计总新闻数
        total_news = cn_count + int_count
        
        # 构建简报
        report = "🌍 全球新闻简报\\n"
        report += f"📅 {datetime.now().strftime("%Y-%m-%d")}\\n\\n"
        
        report += f"📊 统计: 国内 {cn_count} 条，国际 {int_count} 条\\n\\n"
        
        # 只显示最重要的新闻
        important_categories = [
            '国内-政治', '国内-财经', '国内-军事',
            '国际-头条', '国际-财经', '国际-金融数据'
        ]
        
        news_added = 0
        for category in important_categories:
            if category in all_news and all_news[category]:
                news_list = all_news[category]
                if news_list:
                    # 只取第一条
                    news = news_list[0]
                    title = self._shorten_title(news['title'], 40)
                    
                    report += f"📰 {category}:\\n"
                    report += f"• {title}\\n"
                    
                    # 如果有来源和时间，添加
                    if 'source' in news:
                        report += f"  来源: {news['source']}\\n"
                    if 'time' in news:
                        report += f"  时间: {news['time']}\\n"
                    
                    report += "\\n"
                    news_added += 1
                    
                    # 最多显示6条重要新闻
                    if news_added >= 6:
                        break
        
        # 如果新闻太少，添加提示
        if news_added < 3:
            report += "⚠️  今日新闻较少，请稍后查看详细报道\\n"
        
        report += "\\n📱 更多新闻请关注详细报道"
        
        # 确保不超过600字符
        if len(report) > 600:
            report = report[:590] + "...\\n[内容已截断]"
        
        return report
    
    def _shorten_title(self, title, max_length):
        """缩短标题"""
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."
'''

    with open("fixed_report_generator.py", "w", encoding="utf-8") as f:
        f.write(fix_content)
    print("✅ 已创建修复文件: fixed_report_generator.py")
    
    # 2. 创建修复说明
    readme_content = """# 微信推送限制修复说明

## 问题
错误代码: 45047 - out of response count limit
原因: 微信测试号推送次数超限

## 限制说明
1. 每天最多发送100条消息
2. 每分钟最多发送20条消息  
3. 每次推送内容不超过600字符
4. GitHub Actions频繁测试导致快速超限

## 已创建的修复文件
1. `fixed_report_generator.py` - 精简版报告生成器
2. 此说明文档

## 使用修复
1. 在 `run_global_push.py` 中替换:
```python
# 原代码
from enhanced_report_generator import EnhancedReportGenerator

# 改为
from fixed_report_generator import FixedReportGenerator
```

2. 修改生成报告的代码:
```python
# 原代码
generator = EnhancedReportGenerator()
global_report = generate_global_report(all_news, cn_count, int_count)

# 改为
generator = FixedReportGenerator()
global_report = generator.generate_global_report(all_news, cn_count, int_count)
```

## 立即操作
1. 上传修复文件到GitHub
2. 等待24小时让微信限制重置
3. 重新测试GitHub Actions
"""
    
    with open("FIX_WEIXIN_LIMIT.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ 已创建修复说明: FIX_WEIXIN_LIMIT.md")

if __name__ == "__main__":
    analyze_wechat_limit()