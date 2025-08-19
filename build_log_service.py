import aiohttp
import asyncio
from typing import List, Dict, Any
from config import config

class BuildLogService:
    def __init__(self):
        self.api_url = config.BUILD_LOG_API_URL
    
    async def query_build_errors(self, build_log_url: str) -> List[str]:
        """调用外部API查询构建日志中的错误关键字"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "build_log_url": build_log_url
                }
                
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get("errors", [])
                    else:
                        print(f"构建日志API调用失败: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"构建日志服务异常: {e}")
            return []
    
    async def mock_query_build_errors(self, build_log_url: str) -> List[str]:
        """模拟构建日志错误查询（用于测试）"""
        # 模拟API调用延迟
        await asyncio.sleep(1)
        
        # 根据URL返回模拟的错误关键字
        if "jenkins" in build_log_url.lower():
            return [
                "BUILD FAILED",
                "Compilation failed",
                "Missing dependency",
                "Permission denied"
            ]
        elif "gitlab" in build_log_url.lower():
            return [
                "Pipeline failed",
                "Test failure",
                "Docker build error",
                "Memory limit exceeded"
            ]
        else:
            return [
                "Build error",
                "Compilation error",
                "Test failure"
            ]
    
    async def get_build_log_errors_by_inst_id(self, cd_inst_id: str) -> List[str]:
        """根据流水线实例ID查询构建日志错误关键字"""
        print(f"正在查询流水线实例 {cd_inst_id} 的构建日志错误...")
        
        # 模拟API调用延迟
        await asyncio.sleep(1)
        
        # 模拟API调用，返回假数据
        # 在实际环境中，这里应该调用真实的API
        mock_errors = [
            "Build error: Module not found",
            "Compilation error: syntax error at line 45",
            "Test failure: AssertionError in test_user_login",
            "Dependency resolution failed",
            "Timeout: Build process exceeded 30 minutes"
        ]
        
        # 根据实例ID返回不同的错误（模拟）
        if cd_inst_id == "123456":
            return mock_errors[:3]  # 返回前3个错误
        elif cd_inst_id == "789012":
            return mock_errors[2:4]  # 返回第3-4个错误
        else:
            return mock_errors  # 返回所有错误
        
        # 实际API调用示例：
        # try:
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(f"{self.api_url}/build-log/{cd_inst_id}") as response:
        #             if response.status == 200:
        #                 data = await response.json()
        #                 return data.get('errors', [])
        #             else:
        #                 return [f"API调用失败: HTTP {response.status}"]
        # except Exception as e:
        #     return [f"API调用异常: {str(e)}"]
