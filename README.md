# 🧠 AI Knowledge Assistant

> 企业级 AI 知识库助手 — 基于 LangGraph + RAG 架构

## 技术栈

| 层级 | 技术 |
|------|------|
| **框架** | FastAPI |
| **编排** | LangGraph + LangChain |
| **LLM** | OpenAI GPT-4o |
| **向量库** | Qdrant |
| **数据模型** | Pydantic v2 |

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url> && cd ai-knowledge-assistant

# 2. 创建虚拟环境
python -m venv .venv && .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置环境变量
copy .env.example .env  # 编辑 .env 填入实际值

# 5. 启动服务
uvicorn app.main:app --reload --port 8000
```

## 项目结构

```
app/
├── core/              # 配置加载、日志
├── schemas/           # Pydantic 数据模型 & LangGraph 状态
├── services/          # 向量数据库 & LLM 服务
├── agents/            # LangGraph RAG 工作流
├── api/               # FastAPI 路由 (v1)
├── data_processing/   # 文档加载与分块
└── main.py            # 应用入口
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/v1/knowledge/upload` | 上传知识文档 |
| `POST` | `/api/v1/knowledge/search` | 语义搜索 |
| `POST` | `/api/v1/chat` | 知识库问答 |

## License

MIT
