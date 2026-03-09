import logging

logger = logging.getLogger(__name__)

def test_wechat_push(config):
    """测试微信推送"""
    try:
        from wechat_notifier import WeChatNotifier
        
        notifier = WeChatNotifier(config)
        
        # 获取token
        token = notifier.get_access_token()
        print(f"Access Token获取成功: {token[:20]}...")
        
        # 发送简单测试消息
        test_message = "这是一条测试消息\n新闻推送系统已就绪！"
        
        success = notifier.send_text_message(test_message)
        
        if success:
            print("测试消息发送成功！")
            return True
        else:
            print("测试消息发送失败")
            return False
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    import config
    
    notifier_config = {
        'WECHAT_TEST': config.Config.WECHAT_TEST,
        'WECHAT_TEST_APPID': config.Config.WECHAT_TEST_APPID,
        'WECHAT_TEST_SECRET': config.Config.WECHAT_TEST_SECRET,
        'WECHAT_TEST_TOUSER': config.Config.WECHAT_TEST_TOUSER,
    }
    
    test_wechat_push(notifier_config)
