# 重要：如何获取正确的微信ID（OpenID）

## 问题说明

你提供的 `gh_965e782fd227` 是**公众号ID**，不是**你的个人OpenID**。

微信测试号需要的是你的个人OpenID，格式通常是：`o6_bmjrPTlm6_2sgVt7hMZOPfL2M`

## 如何获取你的OpenID

### 方法一：使用在线工具（推荐）

1. 访问微信测试号管理页面：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

2. 找到 **"用户列表"** 部分（页面下方）

3. 在用户列表中找到你的微信号

4. 点击你的微信号，会显示你的OpenID，格式类似：`o6_xxxxxxxxxxxxxxxxxxxxxxxxx`

5. 复制这个OpenID（不是gh_开头的那个）

### 方法二：使用测试号接口

1. 在微信测试号页面，找到 **"接口配置信息"**

2. 配置一个简单的服务器接口

3. 关注测试号后，微信会推送OpenID给你的服务器

## 更新配置文件

获取到正确的OpenID后：

1. 打开 `.env` 文件
2. 找到 `WECHAT_TEST_TOUSER`
3. 将 `gh_965e782fd227` 替换为你的真实OpenID（o6_开头）

```env
WECHAT_TEST_TOUSER=o6_xxxxxxxxxxxxxxxxxxxxx  # 替换为你的真实OpenID
```

4. 保存文件
5. 重新运行程序

## 验证

- 公众号ID：以 `gh_` 开头
- 个人OpenID：以 `o` 开头（如 o6_、o8_ 等）

你现在需要的是个人OpenID！
