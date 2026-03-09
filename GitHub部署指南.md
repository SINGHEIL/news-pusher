# GitHub Actions部署指南

## 🚀 部署步骤（完全免费）

### 第1步：注册GitHub账号

1. 访问：https://github.com
2. 点击"Sign up"注册账号
3. 验证邮箱

### 第2步：创建新仓库

1. 登录后，点击右上角的"+"，选择"New repository"
2. 仓库名称：输入 `news-pusher`（或任意名称）
3. 选择"Public"（公开）
4. 点击"Create repository"

### 第3步：上传代码

选择你熟悉的方式：

**方式A：使用GitHub Desktop（推荐新手）**
1. 下载安装 GitHub Desktop
2. 登录你的GitHub账号
3. 选择"File" -> "Add local repository"
4. 选择你的项目文件夹：`c:/Users/Rihanna/WorkBuddy/Claw`
5. 点击"Publish repository"

**方式B：使用命令行**
```bash
cd c:/Users/Rihanna/WorkBuddy/Claw
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/news-pusher.git
git push -u origin main
```

### 第4步：配置微信密钥

1. 进入你的GitHub仓库页面
2. 点击"Settings" -> "Secrets and variables" -> "Actions"
3. 点击"New repository secret"
4. 添加以下密钥：

| Name | Secret | 值 |
|------|--------|-----|
| WECHAT_APPID | 你的AppID | wx8a7d498abf77cfaf |
| WECHAT_SECRET | 你的Secret | b0780ca63a04f8a5d1765ee87493d201 |
| WECHAT_TOUSER | 你的OpenID | oWJ7k26d6P7dHrOW0D2gGVCRj_3M |

### 第5步：启用Actions

1. 进入仓库，点击"Actions"标签
2. 点击"Daily News Push"工作流
3. 点击"Enable workflow"

### 第6步：测试运行

1. 在Actions页面，点击"Run workflow" -> "Run workflow"
2. 等待运行完成（约1-2分钟）
3. 检查你的微信，应该收到测试消息

## ✅ 完成！

现在系统会：
- **每天上午9:00**自动运行
- 抓取新闻并推送到你的微信
- **你的电脑可以关机**，完全不影响

## 📊 查看运行日志

1. 进入GitHub仓库
2. 点击"Actions"标签
3. 点击最新的运行记录
4. 查看详细日志

## 🔧 手动触发推送

如果想立即推送：
1. 进入"Actions"页面
2. 点击"Run workflow"
3. 点击绿色按钮"Run workflow"

## 💰 费用说明

- GitHub Actions：**完全免费**
- 每月限制：2000分钟（每天只需1分钟，完全够用）

## ⚠️ 注意事项

1. 确保GitHub仓库是Public（公开）
2. 私有仓库的Actions有时间限制
3. 第一次运行可能需要1-2分钟加载环境

---

**部署完成后，你再也不用管了，每天9:00自动收到新闻推送！**
