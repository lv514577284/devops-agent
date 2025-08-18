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
