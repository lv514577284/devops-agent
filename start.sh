#!/bin/bash
echo "启动 DevOps QA Agent..."
echo ""
echo "正在启动服务器..."
uvicorn devops_qa_agent.api.server:app --host 0.0.0.0 --port 8000 --reload
