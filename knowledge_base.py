import json
import os
from typing import List, Dict, Any
from config import config

class KnowledgeBase:
    def __init__(self):
        self.kb_path = config.KNOWLEDGE_BASE_PATH
        self.ensure_kb_directory()
        self.load_knowledge_base()
    
    def ensure_kb_directory(self):
        """确保知识库目录存在"""
        if not os.path.exists(self.kb_path):
            os.makedirs(self.kb_path)
    
    def load_knowledge_base(self):
        """加载知识库数据"""
        self.kb_file = os.path.join(self.kb_path, "knowledge_base.json")
        
        if not os.path.exists(self.kb_file):
            # 创建默认知识库
            self.create_default_knowledge_base()
        
        with open(self.kb_file, 'r', encoding='utf-8') as f:
            self.knowledge_data = json.load(f)
    
    def create_default_knowledge_base(self):
        """创建默认知识库"""
        default_kb = {
            "build_errors": [
                {
                    "keywords": ["BUILD FAILED", "Compilation failed", "编译失败"],
                    "question": "构建失败怎么办？",
                    "answer": "构建失败通常由以下原因引起：1. 代码语法错误 2. 依赖缺失 3. 环境配置问题。建议检查构建日志，定位具体错误位置。"
                },
                {
                    "keywords": ["Missing dependency", "依赖缺失", "package not found"],
                    "question": "依赖缺失如何解决？",
                    "answer": "依赖缺失解决方案：1. 检查package.json或requirements.txt 2. 运行npm install或pip install 3. 清除缓存后重新安装"
                },
                {
                    "keywords": ["Permission denied", "权限不足"],
                    "question": "权限不足怎么处理？",
                    "answer": "权限问题解决方法：1. 检查文件权限 2. 使用sudo命令 3. 修改文件所有者 4. 检查SELinux设置"
                },
                {
                    "keywords": ["Test failure", "测试失败"],
                    "question": "测试失败如何调试？",
                    "answer": "测试失败调试步骤：1. 查看测试日志 2. 检查测试环境 3. 验证测试数据 4. 运行单个测试用例"
                }
            ],
            "general_qa": [
                {
                    "keywords": ["部署", "deploy", "发布"],
                    "question": "如何部署应用？",
                    "answer": "应用部署步骤：1. 构建项目 2. 配置环境变量 3. 启动服务 4. 健康检查 5. 监控运行状态"
                },
                {
                    "keywords": ["性能", "performance", "优化"],
                    "question": "如何优化应用性能？",
                    "answer": "性能优化方法：1. 代码层面优化 2. 数据库查询优化 3. 缓存策略 4. 负载均衡 5. 监控分析"
                }
            ]
        }
        
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump(default_kb, f, ensure_ascii=False, indent=2)
    
    def search_knowledge(self, query: str, error_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """搜索知识库"""
        results = []
        
        # 如果有错误关键字，优先搜索构建错误知识库
        if error_keywords:
            for error_kb in self.knowledge_data.get("build_errors", []):
                for keyword in error_keywords:
                    if any(kw.lower() in keyword.lower() for kw in error_kb["keywords"]):
                        results.append({
                            "type": "build_error",
                            "question": error_kb["question"],
                            "answer": error_kb["answer"],
                            "matched_keyword": keyword
                        })
        
        # 搜索一般知识库
        for general_kb in self.knowledge_data.get("general_qa", []):
            for keyword in general_kb["keywords"]:
                if keyword.lower() in query.lower():
                    results.append({
                        "type": "general",
                        "question": general_kb["question"],
                        "answer": general_kb["answer"],
                        "matched_keyword": keyword
                    })
                    break
        
        return results
    
    def add_knowledge(self, category: str, keywords: List[str], question: str, answer: str):
        """添加知识到知识库"""
        if category not in self.knowledge_data:
            self.knowledge_data[category] = []
        
        new_knowledge = {
            "keywords": keywords,
            "question": question,
            "answer": answer
        }
        
        self.knowledge_data[category].append(new_knowledge)
        
        # 保存到文件
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_data, f, ensure_ascii=False, indent=2)
