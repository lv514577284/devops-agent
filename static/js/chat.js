class ChatApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.websocket = null;
        this.isConnected = false;
        this.isTyping = false;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeWebSocket();
        this.loadTheme();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendMessage');
        this.clearButton = document.getElementById('clearChat');
        this.themeButton = document.getElementById('toggleTheme');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.charCount = document.querySelector('.char-count');
    }
    
    bindEvents() {
        // 发送消息
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 输入框自动调整高度
        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
            this.updateCharCount();
        });
        
        // 清空聊天
        this.clearButton.addEventListener('click', () => this.clearChat());
        
        // 切换主题
        this.themeButton.addEventListener('click', () => this.toggleTheme());
        
        // 窗口大小变化时调整输入框
        window.addEventListener('resize', () => this.adjustTextareaHeight());
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket连接已建立');
            this.isConnected = true;
            this.sendButton.disabled = false;
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket连接已关闭');
            this.isConnected = false;
            this.sendButton.disabled = true;
            
            // 尝试重新连接
            setTimeout(() => {
                if (!this.isConnected) {
                    this.initializeWebSocket();
                }
            }, 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket错误:', error);
            this.showError('连接错误，请刷新页面重试');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status':
                // 状态消息不自动移除，直接添加到流式输出中
                this.appendChunk(data.content);
                break;
            case 'chunk':
                this.appendChunk(data.content);
                break;
            case 'complete':
                this.completeMessage();
                break;
            case 'error':
                this.showError(data.content);
                break;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // 添加用户消息
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        this.updateCharCount();
        
        // 显示助手消息占位符
        this.startTyping();
        
        // 发送WebSocket消息
        if (this.isConnected) {
            this.websocket.send(JSON.stringify({
                message: message
            }));
        } else {
            // 如果WebSocket不可用，使用HTTP API
            await this.sendMessageViaHTTP(message);
        }
    }
    
    async sendMessageViaHTTP(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                // 处理流式响应
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                this.handleStreamData(data);
                            } catch (e) {
                                console.error('解析流数据错误:', e);
                            }
                        }
                    }
                }
            } else {
                throw new Error('请求失败');
            }
        } catch (error) {
            console.error('HTTP请求错误:', error);
            this.showError('发送消息失败，请重试');
            this.completeMessage();
        }
    }
    
    handleStreamData(data) {
        switch (data.type) {
            case 'chunk':
                this.appendChunk(data.content);
                break;
            case 'complete':
                this.completeMessage();
                break;
            case 'error':
                this.showError(data.content);
                this.completeMessage();
                break;
        }
    }
    
    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (role === 'user') {
            avatar.textContent = 'U';
            messageContent.textContent = content;
        } else if (role === 'assistant') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
            messageContent.innerHTML = this.formatMessage(content);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    startTyping() {
        this.isTyping = true;
        this.sendButton.disabled = true;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.id = 'typing-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    appendChunk(chunk) {
        let typingMessage = document.getElementById('typing-message');
        if (!typingMessage) {
            this.startTyping();
            typingMessage = document.getElementById('typing-message');
        }
        
        const messageContent = typingMessage.querySelector('.message-content');
        if (messageContent.querySelector('.typing-dots')) {
            messageContent.innerHTML = '';
        }
        
        // 使用textContent来避免HTML注入问题，然后手动处理换行
        const currentText = messageContent.textContent || '';
        messageContent.textContent = currentText + chunk;
        
        // 手动处理换行符
        messageContent.innerHTML = messageContent.textContent.replace(/\n/g, '<br>');
        
        this.scrollToBottom();
    }
    
    completeMessage() {
        this.isTyping = false;
        this.sendButton.disabled = false;
        
        const typingMessage = document.getElementById('typing-message');
        if (typingMessage) {
            // 移除typing-message的ID，让它成为普通的助手消息
            typingMessage.removeAttribute('id');
            // 格式化消息内容
            const messageContent = typingMessage.querySelector('.message-content');
            if (messageContent) {
                // 获取原始文本内容，避免重复格式化
                const originalText = messageContent.textContent || '';
                messageContent.innerHTML = this.formatMessage(originalText);
            }
        }
    }
    
    showStatusMessage(content) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'status-message';
        statusDiv.textContent = content;
        
        this.chatMessages.appendChild(statusDiv);
        this.scrollToBottom();
        
        // 3秒后自动移除状态消息
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.remove();
            }
        }, 3000);
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'status-message error-message';
        errorDiv.textContent = message;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // 5秒后自动移除错误消息
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    formatMessage(content) {
        // 简单的消息格式化
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    clearChat() {
        if (confirm('确定要清空所有对话吗？')) {
            // 保留系统欢迎消息
            const systemMessage = this.chatMessages.querySelector('.message.system');
            this.chatMessages.innerHTML = '';
            if (systemMessage) {
                this.chatMessages.appendChild(systemMessage);
            }
        }
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // 更新按钮图标
        const icon = this.themeButton.querySelector('i');
        if (newTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // 更新按钮图标
        const icon = this.themeButton.querySelector('i');
        if (savedTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
    
    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        const scrollHeight = this.messageInput.scrollHeight;
        const maxHeight = 120;
        this.messageInput.style.height = Math.min(scrollHeight, maxHeight) + 'px';
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/1000`;
        
        if (count > 900) {
            this.charCount.style.color = '#dc2626';
        } else if (count > 800) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = '';
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
