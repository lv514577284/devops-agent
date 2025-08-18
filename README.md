# 智能问答系统

基于LangGraph 0.3+构建的智能问答系统，支持多轮对话、意图识别、构建日志分析和知识库查询。

## 🚀 功能特性

- **多轮对话**: 支持连续对话，用户可以不断补充问题
- **意图识别**: 自动识别用户问题类型（构建问题 vs 一般问题）
- **构建日志分析**: 针对构建问题，自动请求构建日志链接并分析错误
- **知识库查询**: 基于问题内容匹配相关知识
- **流式输出**: 实时流式显示回答内容
- **WebSocket通信**: 支持实时双向通信
- **现代化UI**: 响应式设计，支持深色/浅色主题切换

## 📋 系统架构

```
用户提问 → 意图识别 → 路由决策 → 处理流程 → 生成回答
    ↓
构建问题 → 请求构建日志 → 分析错误 → 查询知识库 → 生成回答
    ↓
一般问题 → 直接查询知识库 → 生成回答
```

## 🛠️ 技术栈

- **后端**: Python 3.8+, FastAPI, LangGraph 0.3+
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **AI模型**: OpenAI GPT-3.5/4
- **通信**: WebSocket, HTTP API
- **样式**: 现代化CSS，支持深色主题

## 📦 安装部署

### 1. 环境要求

- Python 3.8+
- OpenAI API Key

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 外部API配置
BUILD_LOG_API_URL=http://localhost:8001/api/build-log

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 知识库配置
KNOWLEDGE_BASE_PATH=./knowledge_base

# 流式输出配置
STREAM_DELAY=0.05
```

### 4. 启动系统

```bash
python main.py
```

或者直接运行：

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问系统

打开浏览器访问：http://localhost:8000

## 📁 项目结构

```
build_agent_langgraph/
├── main.py                 # 主启动文件
├── api_server.py           # FastAPI服务器
├── chat_agent.py           # LangGraph聊天智能体
├── config.py               # 配置文件
├── models.py               # 数据模型
├── intent_classifier.py    # 意图识别模块
├── build_log_service.py    # 构建日志服务
├── knowledge_base.py       # 知识库服务
├── llm_service.py          # 大模型服务
├── requirements.txt        # 依赖文件
├── README.md              # 项目文档
├── templates/             # HTML模板
│   └── chat.html
├── static/                # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
└── knowledge_base/        # 知识库数据
    └── knowledge_base.json
```

## 🔧 核心模块说明

### 1. LangGraph智能体 (`chat_agent.py`)

使用LangGraph 0.3+构建的状态图，包含以下节点：

- **意图识别节点**: 分析用户问题类型
- **构建日志请求节点**: 请求用户提供构建日志链接
- **构建日志提取节点**: 从用户消息中提取链接
- **构建错误查询节点**: 调用外部API分析错误
- **知识库搜索节点**: 查询相关知识
- **回答生成节点**: 生成最终回答

### 2. 意图识别 (`intent_classifier.py`)

使用大模型进行意图分类：
- **构建问题**: 涉及编译、构建、CI/CD等
- **一般问题**: 其他技术问题

### 3. 构建日志服务 (`build_log_service.py`)

- 调用外部API分析构建日志
- 提取错误关键字
- 支持模拟模式用于测试

### 4. 知识库 (`knowledge_base.py`)

- JSON格式存储知识
- 支持关键词匹配
- 分类存储（构建错误、一般问答）

### 5. 前端界面

- 现代化响应式设计
- WebSocket实时通信
- 流式输出显示
- 深色/浅色主题切换

## 🎯 使用示例

### 构建问题示例

1. **用户**: "我的Jenkins构建失败了"
2. **系统**: "我检测到您的问题与构建相关。请提供构建日志链接..."
3. **用户**: "https://jenkins.example.com/build/123"
4. **系统**: 分析构建日志 → 查询知识库 → 生成解决方案

### 一般问题示例

1. **用户**: "如何优化应用性能？"
2. **系统**: 直接查询知识库 → 生成回答

## 🔌 API接口

### HTTP API

- `POST /api/chat` - 聊天接口
- `GET /api/sessions/{session_id}` - 获取会话历史
- `DELETE /api/sessions/{session_id}` - 删除会话

### WebSocket API

- `WS /ws/{session_id}` - 实时聊天接口

## 🎨 自定义配置

### 修改知识库

编辑 `knowledge_base/knowledge_base.json`：

```json
{
  "build_errors": [
    {
      "keywords": ["BUILD FAILED", "编译失败"],
      "question": "构建失败怎么办？",
      "answer": "构建失败解决方案..."
    }
  ],
  "general_qa": [
    {
      "keywords": ["性能", "优化"],
      "question": "如何优化应用性能？",
      "answer": "性能优化方法..."
    }
  ]
}
```

### 修改意图识别

在 `intent_classifier.py` 中调整提示词模板。

### 修改UI样式

编辑 `static/css/style.css` 自定义界面样式。

## 🐛 故障排除

### 常见问题

1. **OpenAI API错误**
   - 检查API密钥是否正确
   - 确认账户余额充足

2. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认端口未被占用

3. **知识库加载失败**
   - 检查文件权限
   - 确认JSON格式正确

### 日志查看

启动时查看控制台输出，包含详细的处理步骤信息。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
