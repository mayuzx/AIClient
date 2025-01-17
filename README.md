# 交流、下载编译包 qq群：751913847
# AI 任务执行、调试助手
![image](https://github.com/user-attachments/assets/fc978ca8-d5c1-4e9c-adda-4cb0c64751d8)
![image](https://github.com/user-attachments/assets/1aca50b8-b674-4fff-95f0-7df57f20af76)

一个基于大语言模型的系统调试工具，可以通过自然语言与 AI 交互来执行系统操作和获取信息。

## 功能特点

- 🤖 智能对话：支持与 AI 进行自然语言交互
- 🛠 工具集成：可以执行 PowerShell 工具和系统命令
- 🔄 多配置管理：支持多个 API 配置的保存和切换
- 📝 对话管理：
  - 支持对话历史编辑
  - 可在新窗口中查看对话
  - 一键提取代码块
  - 支持对话内容替换
  - 跨模型对话
- ⚡ 快捷操作：支持自定义常用指令
- 🎨 友好界面：基于 Tkinter 的现代化界面设计

## 安装要求

- Python 3.6+
- PowerShell 5.0+
- 以下 Python 包：
  ```
  tkinter
  requests
  certifi
  ```

## 快速开始

1. 克隆仓库：

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 API：
   - 启动程序
   - 点击"另存为"创建新配置
   - 填入 API 密钥和基础 URL
   - 点击"保存设置"

4. 运行程序：
   ```bash
   python chat_interface.py
   ```

## 使用说明

### 配置管理
- 支持多个 API 配置
- 可以保存、切换和删除配置
- 每个配置包含：API 密钥、基础 URL、模型选择、温度设置等

### 对话功能
- 发送消息：在输入框中输入内容，按回车或点击发送按钮
- 停止生成：在 AI 回复过程中可随时停止
- 查看历史：可以编辑或在新窗口中查看对话历史
- 提取代码：一键提取对话中的所有代码块

### 工具管理
- 支持自定义 PowerShell 工具
- 工具配置保存在 tools_config.json 中
- 可以通过界面添加和管理工具

### 快捷指令
- 支持自定义常用指令
- 通过闪电按钮(⚡)快速访问
- 可以管理和编辑快捷指令列表

## 配置文件说明

- `config.json`: 默认配置文件
- `configs.json`: 多配置存储文件
- `tools_config.json`: 工具配置文件
- `custom_contents.json`: 自定义快捷指令配置

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE) 
