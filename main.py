import schedule
import time
import logging
import signal
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

class ExamNewsScheduler:
    """公考财会新闻定时调度器"""
    
    def __init__(self, config, fetcher, filter, notifier):
        self.config = config
        self.fetcher = fetcher
        self.filter = filter
        self.notifier = notifier
        self.push_time = config.get('PUSH_TIME', '09:00')
        self.running = True
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        logger.info(f"接收到信号 {signum}, 正在停止...")
        self.running = False
    
    def _job(self):
        """定时任务：抓取-筛选-推送"""
        try:
            logger.info(f"执行定时推送任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 1. 抓取新闻
            logger.info("开始抓取新闻...")
            all_news = self.fetcher.fetch_all_news()
            
            # 2. 筛选和格式化
            logger.info("筛选和格式化新闻...")
            filtered_news = self.filter.filter_news(all_news)
            report = self.filter.format_report(filtered_news)
            
            # 3. 推送到微信
            logger.info("推送到微信...")
            success = self.notifier.format_and_send(report)
            
            if success:
                logger.info("定时推送任务完成")
            else:
                logger.error("推送失败")
            
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)
    
    def _run_once(self):
        """立即执行一次推送"""
        logger.info("立即执行推送任务")
        self._job()
    
    def schedule_daily(self):
        """设置每日定时任务"""
        schedule.every().day.at(self.push_time).do(self._job)
        logger.info(f"已设置每日 {self.push_time} 执行推送任务")
    
    def run(self, once: bool = False):
        """运行调度器"""
        if once:
            self._run_once()
            return
        
        logger.info("=" * 50)
        logger.info("公考财会新闻推送系统启动")
        logger.info(f"推送时间: {self.push_time}")
        logger.info("=" * 50)
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("接键盘中断, 正在停止...")
        finally:
            logger.info("调度器已停止")

def main():
    """主函数"""
    import config
    from exam_news_fetcher import ExamNewsFetcher
    from content_filter import ContentFilter
    from wechat_notifier import WeChatNotifier
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, config.Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('news_pusher.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 初始化组件
    fetcher = ExamNewsFetcher()
    filter = ContentFilter(
        use_ai=bool(config.Config.OPENAI_API_KEY),
        api_key=config.Config.OPENAI_API_KEY
    )
    
    notifier_config = {
        'WECHAT_TEST': config.Config.WECHAT_TEST,
        'WECHAT_TEST_APPID': config.Config.WECHAT_TEST_APPID,
        'WECHAT_TEST_SECRET': config.Config.WECHAT_TEST_SECRET,
        'WECHAT_TEST_TOUSER': config.Config.WECHAT_TEST_TOUSER,
        'WECHAT_APPID': config.Config.WECHAT_APPID,
        'WECHAT_SECRET': config.Config.WECHAT_SECRET,
        'WECHAT_TEMPLATE_ID': config.Config.WECHAT_TEMPLATE_ID,
        'WECHAT_TOUSER': config.Config.WECHAT_TOUSER,
    }
    notifier = WeChatNotifier(notifier_config)
    
    # 创建调度器
    scheduler = ExamNewsScheduler(
        config.Config.__dict__,
        fetcher,
        filter,
        notifier
    )
    
    # 设置定时任务
    scheduler.schedule_daily()
    
    # 运行
    scheduler.run()  # 正式运行：每天定时推送
    # scheduler.run(once=True)  # 测试时使用立即执行

if __name__ == "__main__":
    main()
