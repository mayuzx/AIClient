import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import requests
import threading
import urllib3
import certifi
import logging
import subprocess
import os
import re

class AIChatInterface:
    def __init__(self, root):
        # 使用日志捕获警告
        logging.captureWarnings(True)
        
        self.root = root
        self.root.title("AI 调试助手")
        
        # 设置默认窗口大小
        self.root.geometry("1024x768")
        
        # 将窗口居中显示
        self.center_window()
        
        # 初始化空配置
        self.config = {
            'api_key': '',
            'base_url': '',
            'system_prompt': '',
            'temperature': 0.7,
            'model': ''
        }
        
        self.processed_tools = set()
        self.custom_contents = self.load_custom_contents()
        
        # 设置UI
        self.setup_ui()
        
        # 加载配置列表并选择第一个（如果有）
        configs = self.load_configs()
        if configs:
            first_config_name = list(configs.keys())[0]
            self.config = configs[first_config_name]
            # 更新界面
            self.config_var.set(first_config_name)
            self.api_key_var.set(self.config['api_key'])
            self.base_url_var.set(self.config['base_url'])
            self.model_var.set(self.config['model'])
            self.temperature_var.set(str(self.config['temperature']))
    
    def center_window(self):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 获取窗口尺寸
        window_width = 1024  # 默认宽度
        window_height = 768  # 默认高度
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def load_config(self):
        """这个方法不再使用"""
        return {
            'api_key': '',
            'base_url': '',
            'system_prompt': '',
            'temperature': 0.7,
            'model': ''
        }
    
    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)
            
    def setup_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建聊天区域
        self.create_chat_area()
        
        # 创建输入区域
        self.create_input_area()
        
        # 初始化消息历史
        self.messages = []
        if self.config['system_prompt']:
            self.messages.append({"role": "system", "content": self.config['system_prompt']})
    
    def create_toolbar(self):
        # 工具栏框架
        toolbar = ttk.LabelFrame(self.main_frame, text="设置")
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建配置选择框架
        config_frame = ttk.Frame(toolbar)
        config_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # 配置选择下拉框
        ttk.Label(config_frame, text="配置:").pack(side=tk.LEFT, padx=5)
        self.config_var = tk.StringVar()
        self.config_dropdown = ttk.Combobox(config_frame, textvariable=self.config_var)
        self.config_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 配置管理按钮
        ttk.Button(config_frame, text="另存为", command=self.save_as_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(config_frame, text="删除", command=self.delete_config).pack(side=tk.LEFT, padx=2)
        
        # 创建左侧框架
        left_frame = ttk.Frame(toolbar)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # 创建右侧框架
        right_frame = ttk.Frame(toolbar)
        right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # 在左侧框架中添加 API Key 和 Base URL
        # API Key
        api_frame = ttk.Frame(left_frame)
        api_frame.pack(fill=tk.X, expand=True)
        ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT, padx=5)
        self.api_key_var = tk.StringVar(value=self.config['api_key'])
        ttk.Entry(api_frame, textvariable=self.api_key_var, show="*").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加显示/隐藏按钮
        def toggle_api_key_visibility():
            entry = api_frame.winfo_children()[1]  # 获取 Entry 控件
            if entry['show'] == '*':
                entry['show'] = ''
            else:
                entry['show'] = '*'
        
        ttk.Button(api_frame, text="👁", width=3, command=toggle_api_key_visibility).pack(side=tk.LEFT)
        
        # Base URL
        url_frame = ttk.Frame(left_frame)
        url_frame.pack(fill=tk.X, expand=True, pady=(5,0))
        ttk.Label(url_frame, text="Base URL:").pack(side=tk.LEFT, padx=5)
        self.base_url_var = tk.StringVar(value=self.config['base_url'])
        ttk.Entry(url_frame, textvariable=self.base_url_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 在右侧框架中添加 Model、Temperature 和按钮
        # Model
        model_frame = ttk.Frame(right_frame)
        model_frame.pack(fill=tk.X, expand=True)
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar(value=self.config['model'])
        ttk.Entry(model_frame, textvariable=self.model_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Temperature 和按钮
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.pack(fill=tk.X, expand=True, pady=(5,0))
        
        # Temperature
        temp_frame = ttk.Frame(bottom_frame)
        temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT, padx=5)
        self.temperature_var = tk.StringVar(value=str(self.config['temperature']))
        ttk.Entry(temp_frame, textvariable=self.temperature_var, width=10).pack(side=tk.LEFT)
        
        # 按钮
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="编辑系统提示词", command=self.edit_system_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="工具管理", command=self.manage_tools).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="保存设置", command=self.save_settings).pack(side=tk.LEFT, padx=2)
        
        # 更新配置下拉框
        self.update_config_list()
        # 绑定选择事件
        self.config_dropdown.bind('<<ComboboxSelected>>', self.load_selected_config)
    
    def load_configs(self):
        """加载所有配置"""
        try:
            with open('configs.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # 创建默认配置
            default_config = {
                'default': {
                    'api_key': '',
                    'base_url': '',
                    'system_prompt': '',
                    'temperature': 0.7,
                    'model': ''
                }
            }
            self.save_configs(default_config)
            return default_config
    
    def save_configs(self, configs):
        """保存所有配置"""
        with open('configs.json', 'w') as f:
            json.dump(configs, f, indent=4)
    
    def update_config_list(self):
        """更新配置下拉框"""
        configs = self.load_configs()
        self.config_dropdown['values'] = list(configs.keys())
        if not self.config_var.get() and configs:
            self.config_var.set(list(configs.keys())[0])
    
    def load_selected_config(self, event=None):
        """加载选中的配置"""
        config_name = self.config_var.get()
        if config_name:
            configs = self.load_configs()
            if config_name in configs:
                self.config = configs[config_name]
                # 更新界面
                self.api_key_var.set(self.config['api_key'])
                self.base_url_var.set(self.config['base_url'])
                self.model_var.set(self.config['model'])
                self.temperature_var.set(str(self.config['temperature']))
    
    def save_as_config(self):
        """保存为新配置"""
        dialog = tk.Toplevel(self.root)
        dialog.title("保存配置")
        dialog.geometry("300x100")
        
        # 设置对话框为模态
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 禁用最大化按钮
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="配置名称:").pack(padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.pack(fill=tk.X, padx=5)
        
        def save():
            name = name_var.get().strip()
            if name:
                configs = self.load_configs()
                configs[name] = {
                    'api_key': self.api_key_var.get(),
                    'base_url': self.base_url_var.get(),
                    'model': self.model_var.get(),
                    'temperature': float(self.temperature_var.get()),
                    'system_prompt': self.config.get('system_prompt', '')
                }
                self.save_configs(configs)
                self.update_config_list()
                self.config_var.set(name)
                dialog.destroy()
        
        ttk.Button(dialog, text="保存", command=save).pack(pady=10)
        
        # 计算对话框位置使其居中
        def center_dialog():
            dialog.update_idletasks()
            
            # 获取主窗口和对话框的尺寸和位置
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            # 计算居中位置
            x = main_x + (main_width - dialog_width) // 2
            y = main_y + (main_height - dialog_height) // 2
            
            # 设置对话框位置
            dialog.geometry(f"+{x}+{y}")
        
        # 等待窗口创建完成后再居中
        self.root.after(10, center_dialog)
        
        # 设置输入框焦点
        name_entry.focus_set()
    
    def delete_config(self):
        """删除当前配置"""
        config_name = self.config_var.get()
        if config_name:
            if messagebox.askyesno("删除配置", 
                                     f"确定要删除配置 '{config_name}' 吗？"):
                configs = self.load_configs()
                if config_name in configs:
                    del configs[config_name]
                    self.save_configs(configs)
                    self.update_config_list()
    
    def save_settings(self):
        """保存当前设置到当前配置"""
        config_name = self.config_var.get()
        if config_name:
            configs = self.load_configs()
            configs[config_name].update({
                'api_key': self.api_key_var.get(),
                'base_url': self.base_url_var.get(),
                'model': self.model_var.get(),
                'temperature': float(self.temperature_var.get()),
                'system_prompt': self.config.get('system_prompt', '')
            })
            self.save_configs(configs)
            self.config = configs[config_name]
    
    def create_chat_area(self):
        # 创建一个框架来包含聊天区域和按钮
        chat_frame = ttk.Frame(self.main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建按钮框架
        button_frame = ttk.Frame(chat_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # 添加按钮（靠右对齐）
        ttk.Button(button_frame, text="清空对话", command=self.clear_chat).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="编辑历史", command=self.edit_chat_history).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="新窗口打开", command=self.open_in_new_window).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="提取代码", command=self.extract_code).pack(side=tk.RIGHT, padx=5)
        
        # 聊天显示区域
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=20)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
    
    def edit_chat_history(self):
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑聊天历史")
        edit_window.geometry("800x600")
        
        # 设置对话框为模态
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # 允许调整大小
        edit_window.resizable(True, True)
        
        # 创建主框架以支持窗口大小调整
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本编辑区
        edit_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        edit_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 获取当前的聊天内容
        current_text = self.chat_display.get("1.0", tk.END)
        edit_text.insert("1.0", current_text)
        
        def save_changes():
            # 获取编辑后的内容
            new_text = edit_text.get("1.0", tk.END).strip()
            
            # 清空当前显示
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.insert("1.0", new_text + "\n")
            self.chat_display.config(state=tk.DISABLED)
            
            # 重建消息历史
            self.rebuild_messages_from_text(new_text)
            
            # 关闭编辑窗口
            edit_window.destroy()
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=save_changes)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # 计算对话框位置使其居中
        def center_dialog():
            edit_window.update_idletasks()
            
            # 获取主窗口和对话框的尺寸和位置
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            
            dialog_width = edit_window.winfo_width()
            dialog_height = edit_window.winfo_height()
            
            # 计算居中位置
            x = main_x + (main_width - dialog_width) // 2
            y = main_y + (main_height - dialog_height) // 2
            
            # 设置对话框位置
            edit_window.geometry(f"+{x}+{y}")
        
        # 等待窗口创建完成后再居中
        self.root.after(10, center_dialog)
        
        # 设置输入框焦点
        edit_text.focus_set()
    
    def rebuild_messages_from_text(self, text):
        """从编辑后的文本重建消息历史"""
        self.messages = []
        
        # 首先添加system prompt（如果有的话）
        if self.config['system_prompt']:
            self.messages.append({"role": "system", "content": self.config['system_prompt']})
        
        # 解析文本内容重建消息历史
        lines = text.split('\n')
        current_role = None
        current_message = []
        
        for line in lines:
            line = line.strip()
            if line.endswith(':'):  # 发现新的角色标记
                # 保存之前的消息（如果有）
                if current_role and current_message:
                    role = "assistant" if current_role == "Assistant" else "user"
                    self.messages.append({
                        "role": role,
                        "content": '\n'.join(current_message).strip()
                    })
                    current_message = []
                
                # 设置新的角色
                current_role = line[:-1]  # 移除冒号
            elif line and current_role:  # 消息内容
                current_message.append(line)
        
        # 保存最后一条消息
        if current_role and current_message:
            role = "assistant" if current_role == "Assistant" else "user"
            self.messages.append({
                "role": role,
                "content": '\n'.join(current_message).strip()
            })
    
    def create_input_area(self):
        # 输入区域框架
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建一个可调整大小的框架
        input_resize_frame = ttk.Frame(input_frame)
        input_resize_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 文本输入框
        self.input_box = scrolledtext.ScrolledText(input_resize_frame, wrap=tk.WORD, height=3)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加大小调整手柄
        sizer = ttk.Sizegrip(input_resize_frame)
        sizer.pack(side=tk.RIGHT, anchor=tk.SE)
        
        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # 发送/停止按钮
        self.send_button = ttk.Button(button_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=2)
        
        # 自定义内容按钮
        custom_button = ttk.Button(button_frame, text="⚡", width=3, command=self.show_custom_menu)
        custom_button.pack(side=tk.LEFT, padx=2)
        
        # 绑定回车键发送
        self.input_box.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        
        # 添加停止标志
        self.stop_generation = False
    
    def edit_system_prompt(self):
        # 创建新窗口
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("编辑系统提示词")
        prompt_window.geometry("600x400")
        
        # 设置对话框为模态
        prompt_window.transient(self.root)
        prompt_window.grab_set()
        
        # 允许调整大小
        prompt_window.resizable(True, True)
        
        # 创建主框架以支持窗口大小调整
        main_frame = ttk.Frame(prompt_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本编辑区
        prompt_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        prompt_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 设置当前的system prompt
        prompt_text.insert("1.0", self.config['system_prompt'])
        
        def save_prompt():
            # 保存system prompt
            self.config['system_prompt'] = prompt_text.get("1.0", tk.END).strip()
            self.save_config()
            
            # 更新消息历史
            self.messages = []
            if self.config['system_prompt']:
                self.messages.append({"role": "system", "content": self.config['system_prompt']})
            
            # 关闭窗口
            prompt_window.destroy()
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=save_prompt)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # 计算对话框位置使其居中
        def center_dialog():
            prompt_window.update_idletasks()
            
            # 获取主窗口和对话框的尺寸和位置
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            
            dialog_width = prompt_window.winfo_width()
            dialog_height = prompt_window.winfo_height()
            
            # 计算居中位置
            x = main_x + (main_width - dialog_width) // 2
            y = main_y + (main_height - dialog_height) // 2
            
            # 设置对话框位置
            prompt_window.geometry(f"+{x}+{y}")
        
        # 等待窗口创建完成后再居中
        self.root.after(10, center_dialog)
        
        # 设置输入框焦点
        prompt_text.focus_set()
    
    def send_message(self):
        if self.send_button["text"] == "停止":
            self.stop_generation = True
            return
        
        user_message = self.input_box.get("1.0", tk.END).strip()
        if not user_message:
            return
        
        # 清空输入框
        self.input_box.delete("1.0", tk.END)
        
        # 显示用户消息
        self.append_message("You", user_message)
        
        # 添加到消息历史
        self.messages.append({"role": "user", "content": user_message})
        
        # 准备API请求
        url = self.config['base_url']
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        tools_info = ""
        # 加载工具列表并添加到系统提示词中
        try:
            with open('tools_config.json', 'r', encoding='utf-8') as f:
                tools = json.load(f)
                for tool in tools:
                    tools_info += f"- {tool['name']}: {tool['example']}\n"
        except FileNotFoundError:
            tools_info = "没有可用的工具"

        print(tools_info)
        
        # 更新系统提示词，包含工具信息
        if self.messages and self.messages[0]['role'] == 'system':
            system_prompt = self.config['system_prompt'].format(tools=tools_info)
            self.messages[0]['content'] = system_prompt
        else:
            system_prompt = self.config['system_prompt'].format(tools=tools_info)
            self.messages.insert(0, {"role": "system", "content": system_prompt})
        
        data = {
            "messages": self.messages,
            "model": self.config['model'],
            "temperature": self.config['temperature'],
            "stream": True
        }
        
        # 开始新的助手消息
        self.start_new_assistant_message()
        
        # 更改按钮为停止
        self.send_button.config(text="停止")
        self.stop_generation = False
        
        # 在新线程中发送请求
        threading.Thread(target=self.send_request, args=(url, headers, data)).start()
    
    def send_request(self, url, headers, data):
        try:
            # 使用 certifi 提供的证书包
            response = requests.post(
                url,
                json=data,
                headers=headers,
                stream=True,
                verify=certifi.where()  # 使用 certifi 的证书包而不是 verify=False
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data != '[DONE]':
                                try:
                                    json_data = json.loads(data)
                                    content = json_data['choices'][0]['delta'].get('content', '')
                                    if content:
                                        # 使用 after 方法在主线程中更新 UI
                                        self.root.after(0, self.update_assistant_message, content)
                                except json.JSONDecodeError:
                                    continue
                
                # 完成后保存消息到历史
                if hasattr(self, 'current_assistant_message'):
                    self.messages.append({
                        "role": "assistant",
                        "content": self.current_assistant_message
                    })
            else:
                # 处理错误响应
                error_msg = ""
                if response.status_code == 401:
                    error_msg = "API Key 无效或已过期"
                elif response.status_code == 403:
                    error_msg = "API Key 没有权限访问该资源"
                elif response.status_code == 429:
                    error_msg = "请求过于频繁，请稍后再试"
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', f"API调用失败: {response.status_code}")
                    except:
                        error_msg = f"API调用失败: {response.status_code}"
                
                self.root.after(0, self.append_message, "System", error_msg)
                
        except requests.exceptions.RequestException as e:
            self.root.after(0, self.append_message, "System", f"网络请求错误: {str(e)}")
        except Exception as e:
            self.root.after(0, self.update_assistant_message, f"\n请求错误: {str(e)}\n")
        finally:
            # 恢复发送按钮状态
            self.root.after(0, lambda: self.send_button.config(text="发送"))
            self.stop_generation = False
    
    def start_new_assistant_message(self):
        """开始新的助手消息"""
        self.chat_display.config(state=tk.NORMAL)
        # 插入新消息标记
        self.chat_display.insert("end", "\n助手:\n")
        # 记录内容开始位置
        self.current_message_start = self.chat_display.index("end")
        # 插入一个空行作为占位
        self.chat_display.insert("end", "\n")
        self.chat_display.see("end")
        self.chat_display.config(state=tk.DISABLED)
        # 重置当前消息和已处理工具集合
        self.current_assistant_message = ""
        self.processed_tools = set()  # 重置已处理工具集合
    
    def update_assistant_message(self, new_content):
        """更新助手消息的显示并检查工具调用"""
        self.chat_display.config(state=tk.NORMAL)
        
        try:
            # 显示新内容
            self.chat_display.insert("end-1c", new_content)
            self.current_assistant_message += new_content
            
            # 检查是否包含完整的工具调用
            current_message = self.current_assistant_message
            tool_start = current_message.rfind("<tool>")
            tool_end = current_message.find("</tool>", tool_start if tool_start != -1 else 0)
            
            # 只有当找到完整的工具调用标记时才处理
            if tool_start != -1 and tool_end != -1 and tool_end > tool_start:
                # 提取工具调用文本
                tool_text = current_message[tool_start:tool_end + 7]  # +7 是 </tool> 的长度
                
                # 检查这个工具调用是否已经被处理过
                if tool_text not in self.processed_tools:
                    # 提取工具名称和参数
                    tool_content = tool_text[6:-7].strip()  # 移除 <tool> 和 </tool>
                    parts = tool_content.split(maxsplit=1)
                    tool_name = parts[0]
                    tool_args = parts[1] if len(parts) > 1 else ""
                    
                    # 执行工具调用
                    result = self.execute_tool(tool_name, tool_args)
                    
                    # 显示工具执行结果（红色）
                    result_text = f"\n[工具执行结果]\n{result}\n"
                    result_index = self.chat_display.index("end-1c")
                    self.chat_display.insert("end-1c", result_text)
                    
                    # 为结果添加红色标签
                    start_index = f"{result_index} linestart"
                    end_index = f"{result_index} lineend + {len(result.splitlines()) + 1} lines"
                    self.chat_display.tag_add("tool_result", start_index, end_index)
                    self.chat_display.tag_config("tool_result", foreground="red")
                    
                    # 更新消息历史
                    self.current_assistant_message = (
                        current_message[:tool_end + 7] +  # 包含 </tool>
                        result_text
                    )
                    
                    # 将此工具调用标记为已处理
                    self.processed_tools.add(tool_text)
            
            self.chat_display.see("end")
        except Exception as e:
            print(f"Error updating message: {str(e)}")
            error_text = f"\n[错误]\n{str(e)}\n"
            self.chat_display.insert("end-1c", error_text)
            self.current_assistant_message += error_text
        
        self.chat_display.config(state=tk.DISABLED)
    
    def append_message(self, sender, message):
        """添加新消息到聊天显示区域"""
        sender_name = "你" if sender == "You" else "助手" if sender == "Assistant" else "系统"
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{sender_name}:\n{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """清空对话历史"""
        if messagebox.askyesno("确认", "确定要清空所有对话历史吗？"):
            # 清空聊天显示
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # 重置消息历史
            self.messages = []
            if self.config['system_prompt']:
                self.messages.append({"role": "system", "content": self.config['system_prompt']})
            
            # 聚焦到输入框
            self.input_box.focus_set()
    
    def manage_tools(self):
        """工具管理对话框"""
        tools_window = tk.Toplevel(self.root)
        tools_window.title("工具管理")
        tools_window.geometry("800x600")
        
        # 设置对话框为模态
        tools_window.transient(self.root)
        tools_window.grab_set()
        
        # 允许调整大小
        tools_window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(tools_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建工具列表框架
        list_frame = ttk.LabelFrame(main_frame, text="工具列表")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建工具列表
        tools_list = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        tools_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tools_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tools_list.config(yscrollcommand=scrollbar.set)
        
        # 创建编辑区域框架
        edit_frame = ttk.LabelFrame(main_frame, text="工具编辑")
        edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 工具名称
        ttk.Label(edit_frame, text="名称:").pack(anchor=tk.W, padx=5, pady=2)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(edit_frame, textvariable=name_var)
        name_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 工具示例
        ttk.Label(edit_frame, text="示例:").pack(anchor=tk.W, padx=5, pady=2)
        example_text = scrolledtext.ScrolledText(edit_frame, height=4)
        example_text.pack(fill=tk.X, padx=5, pady=2)
        
        # 工具代码
        ttk.Label(edit_frame, text="代码:").pack(anchor=tk.W, padx=5, pady=2)
        code_text = scrolledtext.ScrolledText(edit_frame, height=20)
        code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        def load_tools():
            """加载工具列表"""
            try:
                with open('tools_config.json', 'r', encoding='utf-8') as f:
                    tools = json.load(f)
                    tools_list.delete(0, tk.END)
                    for tool in tools:
                        tools_list.insert(tk.END, tool['name'])
                    return tools
            except FileNotFoundError:
                return []
        
        def save_tools(tools):
            """保存工具列表"""
            with open('tools_config.json', 'w', encoding='utf-8') as f:
                json.dump(tools, f, ensure_ascii=False, indent=4)
        
        def on_select(event):
            """选择工具时的处理"""
            if not tools_list.curselection():
                return
            index = tools_list.curselection()[0]
            tool = tools[index]
            name_var.set(tool['name'])
            example_text.delete('1.0', tk.END)
            example_text.insert('1.0', tool['example'])
            code_text.delete('1.0', tk.END)
            code_text.insert('1.0', tool['code'])
        
        def add_tool():
            """添加新工具"""
            name = "新工具"
            tools.append({
                'name': name,
                'example': '',
                'code': ''
            })
            tools_list.insert(tk.END, name)
            save_tools(tools)
            tools_list.selection_clear(0, tk.END)
            tools_list.selection_set(tk.END)
            tools_list.see(tk.END)
            on_select(None)
        
        def save_tool():
            """保存当前工具"""
            if not tools_list.curselection():
                return
            index = tools_list.curselection()[0]
            tools[index] = {
                'name': name_var.get(),
                'example': example_text.get('1.0', tk.END).strip(),
                'code': code_text.get('1.0', tk.END).strip()
            }
            tools_list.delete(index)
            tools_list.insert(index, name_var.get())
            tools_list.selection_set(index)
            save_tools(tools)
            messagebox.showinfo("成功", "工具保存成功！")
        
        def delete_tool():
            """删除当前工具"""
            if not tools_list.curselection():
                return
            if not messagebox.askyesno("确认", "确定要删除这个工具吗？"):
                return
            index = tools_list.curselection()[0]
            tools.pop(index)
            tools_list.delete(index)
            save_tools(tools)
            clear_form()
        
        def clear_form():
            """清空表单"""
            name_var.set("")
            example_text.delete('1.0', tk.END)
            code_text.delete('1.0', tk.END)
        
        # 按钮框架
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="新建", command=add_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="保存", command=save_tool).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=delete_tool).pack(side=tk.LEFT, padx=2)
        
        # 绑定选择事件
        tools_list.bind('<<ListboxSelect>>', on_select)
        
        # 加载工具列表
        tools = load_tools()
        
        # 计算对话框位置使其居中
        def center_dialog():
            tools_window.update_idletasks()
            
            # 获取主窗口和对话框的尺寸和位置
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            
            dialog_width = tools_window.winfo_width()
            dialog_height = tools_window.winfo_height()
            
            # 计算居中位置
            x = main_x + (main_width - dialog_width) // 2
            y = main_y + (main_height - dialog_height) // 2
            
            # 设置对话框位置
            tools_window.geometry(f"+{x}+{y}")
        
        # 等待窗口创建完成后再居中
        self.root.after(10, center_dialog)
    
    def execute_tool(self, tool_name, args):
        """执行工具调用"""
        try:
            # 加载工具配置
            with open('tools_config.json', 'r', encoding='utf-8') as f:
                tools = json.load(f)
            
            # 从函数定义中查找工具
            function_code = None
            for tool in tools:
                if tool['code'].startswith(f"function {tool_name}"):
                    function_code = tool['code']
                    break
            
            if not function_code:
                return f"错误：找不到工具 '{tool_name}'"
            
            # 构建完整的函数调用
            function_call = f"{tool_name} {args}".strip()
            
            # 创建临时 PowerShell 脚本文件
            script_path = 'temp_script.ps1'
            
            # 构建完整的 PowerShell 脚本
            full_script = f"""
# 设置输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 定义函数
{function_code}

# 执行函数并捕获错误
try {{
    {function_call}
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
"""
            
            # 使用 UTF-8 编码保存脚本
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_script)
            
            # 执行 PowerShell 脚本
            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # 删除临时脚本文件
            try:
                os.remove(script_path)
            except:
                pass
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"错误：{result.stderr.strip()}"
            
        except Exception as e:
            return f"工具执行错误：{str(e)}"
    
    def load_custom_contents(self):
        """加载自定义内容"""
        try:
            with open('custom_contents.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return [
                {"name": "查看系统信息", "content": "请帮我查看当前系统的基本信息"},
                {"name": "查看CPU信息", "content": "请帮我查看CPU的详细信息"},
                {"name": "查看内存状态", "content": "请帮我查看当前系统的内存使用情况"}
            ]
    
    def save_custom_contents(self):
        """保存自定义内容"""
        with open('custom_contents.json', 'w', encoding='utf-8') as f:
            json.dump(self.custom_contents, f, ensure_ascii=False, indent=4)
    
    def show_custom_menu(self):
        """显示自定义内容菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        
        # 添加自定义内容
        for item in self.custom_contents:
            menu.add_command(
                label=item["name"],
                command=lambda content=item["content"]: self.send_custom_content(content)
            )
        
        # 添加分隔线
        menu.add_separator()
        
        # 添加管理选项
        menu.add_command(label="管理自定义内容...", command=self.manage_custom_contents)
        
        # 显示菜单
        try:
            menu.tk_popup(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
        finally:
            menu.grab_release()
    
    def send_custom_content(self, content):
        """发送自定义内容"""
        self.input_box.delete("1.0", tk.END)
        self.input_box.insert("1.0", content)
        self.send_message()
    
    def manage_custom_contents(self):
        """管理自定义内容"""
        dialog = tk.Toplevel(self.root)
        dialog.title("管理自定义内容")
        dialog.geometry("500x400")
        
        # 设置对话框为模态
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 允许调整大小
        dialog.resizable(True, True)
        
        # 创建列表框架
        list_frame = ttk.LabelFrame(dialog, text="自定义内容列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建列表和滚动条
        content_list = tk.Listbox(list_frame, activestyle='none')
        content_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=content_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_list.config(yscrollcommand=scrollbar.set)
        
        # 编辑框架
        edit_frame = ttk.Frame(dialog)
        edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 名称输入
        ttk.Label(edit_frame, text="名称:").pack(side=tk.LEFT)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(edit_frame, textvariable=name_var)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        # 内容输入
        content_frame = ttk.LabelFrame(dialog, text="内容")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, height=5)
        content_text.pack(fill=tk.BOTH, expand=True)
        
        def update_list():
            """更新列表显示"""
            content_list.delete(0, tk.END)
            for item in self.custom_contents:
                content_list.insert(tk.END, item["name"])
        
        def on_select(event=None):
            """选择列表项时的处理"""
            if not content_list.curselection():
                # 如果没有选中项，尝试恢复上一次的选中状态
                if hasattr(content_list, '_last_selection') and content_list._last_selection < content_list.size():
                    content_list.selection_set(content_list._last_selection)
                return
            
            index = content_list.curselection()[0]
            # 保存当前选中的索引
            content_list._last_selection = index
            
            item = self.custom_contents[index]
            name_var.set(item["name"])
            content_text.delete("1.0", tk.END)
            content_text.insert("1.0", item["content"])
        
        def add_item():
            """添加新项目"""
            self.custom_contents.append({
                "name": "新建内容",
                "content": ""
            })
            update_list()
            last_index = len(self.custom_contents) - 1
            content_list.selection_clear(0, tk.END)
            content_list.selection_set(last_index)
            content_list.see(last_index)
            content_list._last_selection = last_index
            on_select()
        
        def save_item():
            """保存当前项目"""
            if not content_list.curselection():
                messagebox.showwarning("警告", "请先选择一个项目！")
                return
            index = content_list.curselection()[0]
            name = name_var.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showwarning("警告", "名称不能为空！")
                return
            if not content:
                messagebox.showwarning("警告", "内容不能为空！")
                return
            
            self.custom_contents[index] = {
                "name": name,
                "content": content
            }
            update_list()
            content_list.selection_set(index)
            content_list._last_selection = index
            self.save_custom_contents()
            messagebox.showinfo("成功", "保存成功！")
        
        def delete_item():
            """删除当前项目"""
            if not content_list.curselection():
                messagebox.showwarning("警告", "请先选择一个项目！")
                return
            if not messagebox.askyesno("确认", "确定要删除这个内容吗？"):
                return
            index = content_list.curselection()[0]
            self.custom_contents.pop(index)
            update_list()
            self.save_custom_contents()
            # 清空编辑区
            name_var.set("")
            content_text.delete("1.0", tk.END)
            # 选中下一个项目（如果有的话）
            if content_list.size() > 0:
                next_index = min(index, content_list.size() - 1)
                content_list.selection_set(next_index)
                content_list._last_selection = next_index
                on_select()
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="新建", command=add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="保存", command=save_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=delete_item).pack(side=tk.LEFT, padx=2)
        
        # 绑定选择事件
        content_list.bind('<<ListboxSelect>>', on_select)
        
        # 更新列表显示
        update_list()
        
        # 计算对话框位置使其居中
        def center_dialog():
            dialog.update_idletasks()
            
            # 获取主窗口和对话框的尺寸和位置
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            # 计算居中位置
            x = main_x + (main_width - dialog_width) // 2
            y = main_y + (main_height - dialog_height) // 2
            
            # 设置对话框位置
            dialog.geometry(f"+{x}+{y}")
        
        # 等待窗口创建完成后再居中
        self.root.after(10, center_dialog)
    
    def open_in_new_window(self):
        """在新窗口中打开当前对话"""
        # 创建新窗口
        dialog_window = tk.Toplevel(self.root)
        
        # 获取当前配置名称
        config_name = self.config_var.get() or "未命名配置"
        dialog_window.title(f"对话查看 - {config_name}")
        dialog_window.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(dialog_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # 添加替换按钮
        def replace_main_content():
            if messagebox.askyesno("确认", "确定要用此对话内容替换主窗口的内容吗？"):
                # 清空主窗口内容
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("1.0", tk.END)
                
                # 先配置主窗口的标签
                self.chat_display.tag_configure("tool_result", foreground="red")
                
                # 复制内容到主窗口
                self.chat_display.insert("1.0", text_area.get("1.0", tk.END))
                
                # 复制标签范围
                for tag in text_area.tag_names():
                    if tag != "sel":  # 跳过选择标签
                        try:
                            ranges = text_area.tag_ranges(tag)
                            for i in range(0, len(ranges), 2):
                                start = self.chat_display.index(ranges[i])
                                end = self.chat_display.index(ranges[i+1])
                                self.chat_display.tag_add(tag, start, end)
                        except Exception as e:
                            print(f"Error copying tag {tag}: {str(e)}")
                
                self.chat_display.config(state=tk.DISABLED)

        ttk.Button(button_frame, text="替换到主窗口", command=replace_main_content).pack(side=tk.LEFT, padx=5)
        
        # 创建文本显示区域
        text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # 配置工具结果标签
        text_area.tag_configure("tool_result", foreground="red")
        
        # 复制当前对话内容
        text_area.insert("1.0", self.chat_display.get("1.0", tk.END))
        
        # 复制所有标签范围
        for tag in self.chat_display.tag_names():
            if tag != "sel":  # 跳过选择标签
                try:
                    ranges = self.chat_display.tag_ranges(tag)
                    for i in range(0, len(ranges), 2):
                        start = text_area.index(ranges[i])
                        end = text_area.index(ranges[i+1])
                        text_area.tag_add(tag, start, end)
                except Exception as e:
                    print(f"Error copying tag {tag}: {str(e)}")
        
        text_area.config(state=tk.DISABLED)
        
        # 计算窗口位置使其错开显示
        def position_window():
            dialog_window.update_idletasks()
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            offset = len([w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]) * 30
            dialog_window.geometry(f"+{main_x + offset}+{main_y + offset}")
        
        # 等待窗口创建完成后再定位
        self.root.after(10, position_window)
    
    def extract_code(self):
        """提取对话中的代码块"""
        # 获取当前对话内容
        content = self.chat_display.get("1.0", tk.END)
        
        # 使用正则表达式查找所有代码块
        # 匹配 ```language 和 ``` 之间的内容
        code_blocks = re.finditer(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        # 记录找到的代码块数量
        block_count = 0
        
        # 遍历所有代码块
        for match in code_blocks:
            block_count += 1
            language = match.group(1) or "text"  # 如果没有指定语言，默认为text
            code = match.group(2).strip()
            
            # 为每个代码块创建新窗口
            code_window = tk.Toplevel(self.root)
            code_window.title(f"代码块 {block_count} - {language}")
            code_window.geometry("600x400")
            
            # 创建主框架
            main_frame = ttk.Frame(code_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建文本显示区域
            text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
            text_area.pack(fill=tk.BOTH, expand=True)
            
            # 插入代码
            text_area.insert("1.0", code)
            
            # 设置为只读
            text_area.config(state=tk.DISABLED)
            
            # 计算窗口位置使其错开显示
            def position_window(window, index):
                window.update_idletasks()
                main_x = self.root.winfo_x()
                main_y = self.root.winfo_y()
                offset = 30 * index
                window.geometry(f"+{main_x + offset}+{main_y + offset}")
            
            # 等待窗口创建完成后再定位
            self.root.after(10, lambda w=code_window, i=block_count: position_window(w, i))
        
        # 如果没有找到代码块，显示提示
        if block_count == 0:
            messagebox.showinfo("提示", "未找到代码块")

if __name__ == "__main__":
    root = tk.Tk()
    app = AIChatInterface(root)
    root.mainloop() 