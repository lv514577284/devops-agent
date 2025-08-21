# DevOps QA Agent - 智能问答系统

一个基于LangGraph和FastAPI的智能问答系统，专门用于解决DevOps相关问题。系统支持多轮对话、意图识别、构建日志分析和知识库查询。系统能够根据问题类型智能处理：构建类型问题需要流水线实例ID，非构建类型问题直接查询知识库。

## 🚀 功能特性

- **多轮对话**: 支持连续对话，用户可以不断补充问题，系统自动保持对话上下文
- **意图识别**: 自动识别用户问题类型（构建问题 vs 一般问题）
- **构建日志分析**: 针对构建问题，根据流水线实例ID查询构建日志错误
- **知识库查询**: 基于问题内容匹配相关知识
- **流式输出**: 实时流式显示回答内容
- **WebSocket通信**: 支持实时双向通信
- **现代化UI**: 响应式设计，支持深色/浅色主题切换
- **智能路由**: 构建问题必须提供cdInstId，非构建问题直接处理

## 📋 系统架构

```
用户提问 → 意图识别 → 路由决策 → 处理流程 → 生成回答
    ↓
构建问题 → 检查cdInstId → 查询构建日志错误 → 查询知识库 → 生成回答
    ↓
一般问题 → 直接查询知识库 → 生成回答
```

## 🛠️ 技术栈

- **后端**: Python 3.13+, FastAPI, LangGraph
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **AI模型**: 百炼云 qwq-32b
- **通信**: WebSocket, HTTP API
- **样式**: 现代化CSS，支持深色主题

## 📦 安装部署

### 1. 环境要求

- Python 3.13+
- 百炼云 API Key

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# 百炼云配置
OPENAI_API_KEY=your_dashscope_api_key_here
OPENAI_MODEL=qwq-32b

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
# 方式1：使用新的启动文件
python run.py

# 方式2：使用包安装方式
pip install -e .
devops-qa-agent

# 方式3：直接使用uvicorn（推荐）
uvicorn devops_qa_agent.api.server:app --host 0.0.0.0 --port 8000 --reload

# 方式4：使用启动脚本
# Windows: 双击 start.bat 或运行 ./start.bat
# Linux/Mac: ./start.sh

# 方式5：VSCode调试
# 1. 创建.vscode/launch.json文件（已创建）
# 2. 点击F5键启动
# 3. 打断点，调用接口

# 杀死本地python服务
tasklist | findstr "python.exe"
```

### 5. 访问系统

打开浏览器访问：http://localhost:8000

## 📁 项目结构

```
devops-qa-agent/
├── requirements.txt             # 依赖包列表
├── setup.py                     # 包安装配置
├── pyproject.toml              # 项目配置文件
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
├── run.py                      # 启动文件
├── start.bat                   # Windows启动脚本
├── start.sh                    # Linux/Mac启动脚本
├── test_imports.py             # 导入测试脚本
├── devops_qa_agent/            # 主包目录（PEP 8标准）
│   ├── __init__.py             # 包初始化文件
│   ├── main.py                 # 应用入口点
│   ├── models.py               # 数据模型
│   ├── config/                 # 配置管理目录
│   │   ├── __init__.py         # 配置包初始化
│   │   └── settings.py         # 主配置文件
│   ├── api/                    # API相关模块
│   │   ├── __init__.py
│   │   └── server.py           # FastAPI服务器
│   ├── services/               # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── chat_service.py     # 聊天服务
│   │   ├── llm_service.py      # LLM服务
│   │   ├── build_log_service.py # 构建日志服务
│   │   └── intent_service.py   # 意图识别服务
│   ├── knowledge/              # 知识库相关
│   │   ├── __init__.py
│   │   ├── base.py             # 知识库基础类
│   │   └── data/               # 知识库数据
│   │       └── knowledge_base.json
│   ├── static/                 # 静态资源
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── chat.js
│   └── templates/              # 模板文件
│       └── chat.html
├── tests/                      # 测试目录
├── docs/                       # 文档目录
└── scripts/                    # 脚本目录
```
├── build_log_service.py    # 构建日志服务
├── knowledge_base.py       # 知识库服务
├── llm_service.py          # 大模型服务
├── requirements.txt        # 依赖文件
├── README.md              # 项目文档
├── env_example.txt         # 环境变量示例
├── templates/             # HTML模板
│   └── chat.html
├── static/                # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
├── knowledge_base/        # 知识库数据
│   └── knowledge_base.json
└── myenv/                 # Python虚拟环境
```

## 🔧 核心模块说明

## 🎯 核心特性

### 智能路由机制
系统根据问题类型采用不同的处理策略：

1. **构建类型问题**：
   - 必须提供 `cdInstId`（流水线实例ID）
   - 如果没有提供，系统会循环对话直到获得ID
   - 获得ID后，查询构建日志错误，结合知识库生成解决方案

2. **非构建类型问题**：
   - 直接查询知识库
   - 将用户问题和知识库内容传给大模型生成回答

### 流式输出支持
- API接口支持Server-Sent Events (SSE)流式返回
- Web页面支持WebSocket实时通信
- 提供实时的处理步骤反馈

### 实例ID提取
- 自动从用户消息中提取数字ID（6位或更多数字）
- 支持多种ID格式
- 智能确认和继续处理

### 1. LangGraph智能体 (`chat_agent.py`)

使用LangGraph构建的状态图，包含以下节点：

- **意图识别节点**: 分析用户问题类型
- **构建日志请求节点**: 检查是否提供cdInstId
- **等待实例ID节点**: 循环等待用户提供流水线实例ID
- **构建错误查询节点**: 根据实例ID查询构建日志错误
- **知识库搜索节点**: 查询相关知识
- **回答生成节点**: 生成最终回答

### 2. 意图识别 (`intent_classifier.py`)

使用大模型进行意图分类：
- **构建问题**: 涉及编译、构建、CI/CD等
- **一般问题**: 其他技术问题

### 3. 构建日志服务 (`build_log_service.py`)

- 根据流水线实例ID查询构建日志错误
- 提取错误关键字
- 支持模拟模式用于测试
- 提供 `get_build_log_errors_by_inst_id()` 方法

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

### API接口调用示例

#### 构建问题（需要cdInstId）
```json
{
    "message": "{\"problemType\": \"构建\", \"cdInstId\": \"123456\", \"problemDesc\": \"我的构建为什么出错了\"}",
    "session_id": "18bf3db5-0306-446b-a9bb-8acecd073529"
}
```

#### 非构建问题
```json
{
    "message": "{\"problemType\": \"其他\",  \"problemDesc\": \"我的为什么出错了\"}",
    "session_id": "18bf3db5-0306-446b-a9bb-8acecd073529"
}
```

### Web页面使用示例

#### 构建问题示例
1. **用户**: "我的Jenkins构建失败了"
2. **系统**: "为了帮您分析构建问题，请提供流水线实例ID (cdInstId)"
3. **用户**: "123456"
4. **系统**: 查询构建日志错误 → 查询知识库 → 生成解决方案

#### 一般问题示例
1. **用户**: "如何优化应用性能？"
2. **系统**: 直接查询知识库 → 生成回答

## 🔌 API接口

### HTTP API

- `POST /api/chat` - 聊天接口（支持流式返回）
- `GET /api/sessions/{session_id}` - 获取会话历史
- `DELETE /api/sessions/{session_id}` - 删除会话

#### 请求参数
- `message`: 用户消息
- `session_id`: 会话ID（可选）
- `problemType`: 问题类型（可选）
- `cdInstId`: 流水线实例ID（可选）
- `problemDesc`: 问题描述（可选）

### WebSocket API

- `WS /ws/{session_id}` - 实时聊天接口

## 🎨 自定义配置

### 修改知识库

编辑 `knowledge_base/knowledge_base.json`：

```json
[
  {
    "question": "构建失败怎么办？",
    "answer": "构建失败解决方案...",
    "keywords": ["BUILD FAILED", "编译失败"]
  },
  {
    "question": "如何优化应用性能？",
    "answer": "性能优化方法...",
    "keywords": ["性能", "优化"]
  }
]
```

### 修改意图识别

在 `intent_classifier.py` 中调整提示词模板。

### 修改UI样式

编辑 `static/css/style.css` 自定义界面样式。

## 🐛 故障排除

### 常见问题

1. **百炼云 API错误**
   - 检查API密钥是否正确
   - 确认账户余额充足

2. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认端口未被占用

3. **知识库加载失败**
   - 检查文件权限
   - 确认JSON格式正确

4. **PowerShell执行策略错误**
   - 如果遇到脚本执行被禁止的错误，可以使用cmd或直接使用虚拟环境中的可执行文件

5. **uvicorn模块导入错误**
   - 错误信息：`Could not import module "api_server"`
   - 原因：项目重构后，文件路径已更改
   - 解决方案：使用新的启动命令 `uvicorn devops_qa_agent.api.server:app --host 0.0.0.0 --port 8000 --reload`

### 日志查看

启动时查看控制台输出，包含详细的处理步骤信息。

## 🛠️ 开发指南

### 测试导入

```bash
python test_imports.py
```

### 代码格式化

项目使用 `black` 和 `isort` 进行代码格式化：

```bash
black devops_qa_agent/
isort devops_qa_agent/
```

### 项目结构说明

项目已按照PEP 8标准重构，主要改进：

- **包结构规范化**: 创建了主包 `devops_qa_agent/`，按功能模块分组
- **文件命名规范化**: 使用下划线命名，如 `chat_service.py`
- **模块职责分离**: 配置层、API层、服务层、知识库层分离
- **资源文件组织**: 静态文件和模板文件移到包内部
- **开发工具配置**: 添加了 `setup.py`、`pyproject.toml` 等配置文件

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
