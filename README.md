# 每日公考与财会动态追踪器

每日定时推送广东公考、横琴金融政策、财会专业相关的新闻资讯到你的微信。

## 功能特点

- 🕐 **定时推送**：每天上午9:00自动推送
- 📰 **多源抓取**：从广东人事考试网、横琴官网、财政部等官方渠道抓取
- 🎯 **智能筛选**：自动筛选与公考、政策、财会相关的内容
- 📝 **精炼摘要**：每条新闻提炼核心事实和备考关联度
- 💬 **微信推送**：通过微信公众号接口推送消息

## 项目结构

```
Claw/
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── exam_news_fetcher.py   # 新闻抓取模块
├── content_filter.py      # 内容筛选和摘要生成
├── wechat_notifier.py     # 微信推送模块
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量示例
└── README.md             # 项目文档
```

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下关键配置：

#### 微信配置（二选一）

**方式一：使用微信测试号（推荐测试用）**

```
WECHAT_TEST=True
WECHAT_TEST_APPID=your_test_appid
WECHAT_TEST_SECRET=your_test_secret
WECHAT_TEST_TOUSER=your_openid
```

**方式二：使用正式微信公众号**

```
WECHAT_TEST=False
WECHAT_APPID=your_appid
WECHAT_SECRET=your_secret
WECHAT_TEMPLATE_ID=your_template_id
WECHAT_TOUSER=your_openid
```

#### 其他配置

```
PUSH_TIME=09:00
OPENAI_API_KEY=your_openai_key  # 可选，用于AI智能摘要
LOG_LEVEL=INFO
```

## 获取微信配置信息

### 微信测试号（推荐）

1. 访问：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
2. 扫码登录后，获取 `appID` 和 `appsecret`
3. 在测试号页面，找到你的微信ID（openid）

### 正式微信公众号

1. 注册微信公众号
2. 在微信公众平台获取 AppID 和 AppSecret
3. 创建模板消息，获取模板ID
4. 获取用户的 OpenID

## 使用方法

### 启动程序

```bash
python main.py
```

程序会启动定时任务，每天9:00自动推送新闻。

### 测试推送

如需立即测试推送功能，修改 `main.py` 文件最后一行：

```python
# 将这行注释掉
# scheduler.run()

# 改为立即执行一次
scheduler.run(once=True)
```

## 推送内容示例

```
📅 每日财会备考简报 - 2026年03月09日
==================================================

📍 **公考热点**
------------------------------

1. 广东省2026年公务员招录公告
   来源: 广东省人事考试网
   核心事实：广东省发布2026年公务员招录计划
   备考关联：可作为面试素材
   链接: http://...

📍 **政策速递**
------------------------------

1. 横琴粤澳深度合作区金融开放新政
   来源: 横琴粤澳深度合作区
   核心事实：横琴出台金融开放新政策
   备考关联：关注政策变化
   链接: http://...

📍 **专业课更新**
------------------------------

1. 会计准则最新更新解读
   来源: 财政部官网
   核心事实：财政部发布会计准则更新
   备考关联：可作行测/专业笔试
   链接: http://...

==================================================
总计: 6 条
==================================================
```

## 新闻来源

系统会从以下渠道抓取新闻：

### 公考类
- 广东省人事考试网
- 珠海市人力资源和社会保障局
- 横琴粤澳深度合作区

### 政策类
- 财政部官网
- 中国会计报
- 广东省财政厅

### 综合类
- 人民日报
- 新华社

## 自定义配置

### 修改推送时间

在 `.env` 文件中修改：

```
PUSH_TIME=08:30  # 改为早上8:30推送
```

### 添加AI智能摘要

填写 OpenAI API Key：

```
OPENAI_API_KEY=sk-your-api-key
```

系统会使用AI为每条新闻生成更智能的摘要。

## 常见问题

### 1. 推送失败

检查：
- 微信配置是否正确
- 网络连接是否正常
- 查看日志文件 `news_pusher.log`

### 2. 抓取不到新闻

可能原因：
- 网站结构变化
- 网络访问受限
- 查看日志获取详细错误信息

### 3. 定时任务不执行

确保：
- 程序保持运行状态
- 时区设置正确
- 检查 PUSH_TIME 格式是否为 HH:MM

## 日志

程序运行日志保存在 `news_pusher.log` 文件中，包含：
- 抓取记录
- 筛选结果
- 推送状态
- 错误信息

## 后台运行

### Linux/Mac

```bash
nohup python main.py > /dev/null 2>&1 &
```

### Windows

使用任务计划程序或第三方工具如：
- Task Scheduler
- NSSM (Non-Sucking Service Manager)
- PyWin32

## 停止程序

按 `Ctrl + C` 安全停止程序。

## 开发说明

### 添加新的新闻源

在 `exam_news_fetcher.py` 的 `__init__` 方法中添加新的源：

```python
self.sources = {
    '新分类': {
        '网站名称': 'https://www.example.com'
    }
}
```

然后创建相应的解析方法。

### 修改筛选规则

在 `content_filter.py` 的 `keywords` 字典中添加或修改关键词：

```python
self.keywords = {
    '分类': ['关键词1', '关键词2']
}
```

## 许可证

MIT License

## 技术支持

如有问题，请查看日志文件或联系开发者。
