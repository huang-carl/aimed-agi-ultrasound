/**
 * AIMED 超人 - 统一客服机器人
 * 集成到所有页面，提供 AI 客服支持
 */

(function() {
    'use strict';

    // ============================================
    // 配置
    // ============================================
    const CONFIG = {
        apiEndpoint: '/api/chat',
        position: 'bottom-right', // bottom-right, bottom-left
        theme: {
            primary: '#2563eb',
            primaryDark: '#1d4ed8',
            accent: '#10b981',
            bg: '#ffffff',
            text: '#1e293b',
            textLight: '#64748b',
            border: '#e2e8f0',
            shadow: 'rgba(0,0,0,0.15)',
        },
        welcomeMessage: '你好！我是小菲同学 🤖\n\n有什么可以帮助你的？\n\n• 产品咨询\n• 技术支持\n• 诊断服务\n• 合作洽谈',
        typingText: '超人正在思考...',
        placeholder: '输入消息...',
        title: '小菲同学 🤖',
        subtitle: 'AIMED AI 助手 · 7×24 在线',
    };

    // ============================================
    // 状态
    // ============================================
    let isOpen = false;
    let conversationHistory = [];
    let isTyping = false;

    // ============================================
    // 创建 DOM 元素
    // ============================================
    function createBotUI() {
        // 检查是否已存在
        if (document.getElementById('aimed-bot-container')) return;

        const container = document.createElement('div');
        container.id = 'aimed-bot-container';
        container.innerHTML = `
            <!-- 悬浮按钮 -->
            <div id="aimed-bot-toggle" onclick="AIMEDBot.toggle()" title="${CONFIG.title}">
                <div class="aimed-bot-icon">🤖</div>
                <div class="aimed-bot-badge">1</div>
            </div>

            <!-- 聊天窗口 -->
            <div id="aimed-bot-window">
                <!-- 头部 -->
                <div class="aimed-bot-header">
                    <div class="aimed-bot-header-info">
                        <div class="aimed-bot-avatar">🤖</div>
                        <div>
                            <div class="aimed-bot-title">${CONFIG.title}</div>
                            <div class="aimed-bot-subtitle">${CONFIG.subtitle}</div>
                        </div>
                    </div>
                    <button class="aimed-bot-close" onclick="AIMEDBot.toggle()">✕</button>
                </div>

                <!-- 消息区域 -->
                <div class="aimed-bot-messages" id="aimed-bot-messages">
                    <div class="aimed-bot-message bot">
                        <div class="aimed-bot-msg-avatar">🤖</div>
                        <div class="aimed-bot-msg-content">
                            <div class="aimed-bot-msg-text">${CONFIG.welcomeMessage.replace(/\n/g, '<br>')}</div>
                            <div class="aimed-bot-msg-time">${getTime()}</div>
                        </div>
                    </div>
                </div>

                <!-- 快捷问题 -->
                <div class="aimed-bot-quick-questions" id="aimed-bot-quick">
                    <button onclick="AIMEDBot.sendQuick('口服造影剂有什么特点？')">💊 造影剂特点</button>
                    <button onclick="AIMEDBot.sendQuick('AI 诊断怎么用？')">🤖 AI 诊断</button>
                    <button onclick="AIMEDBot.sendQuick('龙脑抑菌液是什么？')">🌿 龙脑抑菌液</button>
                    <button onclick="AIMEDBot.sendQuick('如何合作？')">🤝 合作洽谈</button>
                </div>

                <!-- 输入区域 -->
                <div class="aimed-bot-input-area">
                    <input type="text" id="aimed-bot-input" placeholder="${CONFIG.placeholder}" onkeydown="AIMEDBot.handleKey(event)">
                    <button onclick="AIMEDBot.send()" id="aimed-bot-send-btn">➤</button>
                </div>
            </div>
        `;

        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            /* 容器 */
            #aimed-bot-container {
                position: fixed;
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            }

            /* 悬浮按钮 */
            #aimed-bot-toggle {
                position: fixed;
                ${CONFIG.position === 'bottom-right' ? 'right: 24px;' : 'left: 24px;'}
                bottom: 24px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, ${CONFIG.theme.primary} 0%, #7c3aed 100%);
                box-shadow: 0 4px 20px ${CONFIG.theme.shadow};
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
                z-index: 9999;
            }
            #aimed-bot-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 28px ${CONFIG.theme.shadow};
            }
            .aimed-bot-icon {
                font-size: 28px;
            }
            .aimed-bot-badge {
                position: absolute;
                top: -4px;
                right: -4px;
                width: 22px;
                height: 22px;
                border-radius: 50%;
                background: #ef4444;
                color: white;
                font-size: 12px;
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: aimed-bot-pulse 2s infinite;
            }
            @keyframes aimed-bot-pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.2); }
            }

            /* 聊天窗口 */
            #aimed-bot-window {
                position: fixed;
                ${CONFIG.position === 'bottom-right' ? 'right: 24px;' : 'left: 24px;'}
                bottom: 100px;
                width: 380px;
                height: 520px;
                background: ${CONFIG.theme.bg};
                border-radius: 16px;
                box-shadow: 0 8px 40px ${CONFIG.theme.shadow};
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 9998;
                animation: aimed-bot-slide-up 0.3s ease-out;
            }
            @keyframes aimed-bot-slide-up {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            #aimed-bot-window.show {
                display: flex;
            }

            /* 头部 */
            .aimed-bot-header {
                background: linear-gradient(135deg, ${CONFIG.theme.primary} 0%, #7c3aed 100%);
                color: white;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .aimed-bot-header-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .aimed-bot-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(255,255,255,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            .aimed-bot-title {
                font-weight: 600;
                font-size: 1em;
            }
            .aimed-bot-subtitle {
                font-size: 0.75em;
                opacity: 0.8;
            }
            .aimed-bot-close {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }
            .aimed-bot-close:hover {
                background: rgba(255,255,255,0.3);
            }

            /* 消息区域 */
            .aimed-bot-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                background: #f8fafc;
            }
            .aimed-bot-message {
                display: flex;
                gap: 8px;
                margin-bottom: 12px;
                animation: aimed-bot-fade-in 0.3s ease-out;
            }
            @keyframes aimed-bot-fade-in {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .aimed-bot-message.user {
                flex-direction: row-reverse;
            }
            .aimed-bot-msg-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: linear-gradient(135deg, ${CONFIG.theme.primary} 0%, #7c3aed 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                flex-shrink: 0;
            }
            .aimed-bot-message.user .aimed-bot-msg-avatar {
                background: ${CONFIG.theme.accent};
            }
            .aimed-bot-msg-content {
                max-width: 75%;
            }
            .aimed-bot-msg-text {
                padding: 10px 14px;
                border-radius: 12px;
                font-size: 0.9em;
                line-height: 1.5;
                word-wrap: break-word;
            }
            .aimed-bot-message.bot .aimed-bot-msg-text {
                background: white;
                color: ${CONFIG.theme.text};
                border: 1px solid ${CONFIG.theme.border};
            }
            .aimed-bot-message.user .aimed-bot-msg-text {
                background: ${CONFIG.theme.primary};
                color: white;
            }
            .aimed-bot-msg-time {
                font-size: 0.7em;
                color: ${CONFIG.theme.textLight};
                margin-top: 4px;
                padding: 0 4px;
            }
            .aimed-bot-message.user .aimed-bot-msg-time {
                text-align: right;
            }

            /* 打字指示器 */
            .aimed-bot-typing {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 10px 14px;
                background: white;
                border-radius: 12px;
                border: 1px solid ${CONFIG.theme.border};
                width: fit-content;
            }
            .aimed-bot-typing-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: ${CONFIG.theme.textLight};
                animation: aimed-bot-typing 1.4s infinite;
            }
            .aimed-bot-typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .aimed-bot-typing-dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes aimed-bot-typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-6px); }
            }

            /* 快捷问题 */
            .aimed-bot-quick-questions {
                padding: 8px 16px;
                background: white;
                border-top: 1px solid ${CONFIG.theme.border};
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
            .aimed-bot-quick-questions button {
                padding: 4px 10px;
                background: #eff6ff;
                color: ${CONFIG.theme.primary};
                border: 1px solid #bfdbfe;
                border-radius: 14px;
                font-size: 0.75em;
                cursor: pointer;
                transition: all 0.2s;
                white-space: nowrap;
            }
            .aimed-bot-quick-questions button:hover {
                background: ${CONFIG.theme.primary};
                color: white;
                border-color: ${CONFIG.theme.primary};
            }

            /* 输入区域 */
            .aimed-bot-input-area {
                padding: 12px 16px;
                background: white;
                border-top: 1px solid ${CONFIG.theme.border};
                display: flex;
                gap: 8px;
            }
            .aimed-bot-input-area input {
                flex: 1;
                padding: 10px 14px;
                border: 1px solid ${CONFIG.theme.border};
                border-radius: 20px;
                font-size: 0.9em;
                outline: none;
                transition: border-color 0.2s;
            }
            .aimed-bot-input-area input:focus {
                border-color: ${CONFIG.theme.primary};
            }
            .aimed-bot-input-area button {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: ${CONFIG.theme.primary};
                color: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.2s;
            }
            .aimed-bot-input-area button:hover {
                background: ${CONFIG.theme.primaryDark};
            }
            .aimed-bot-input-area button:disabled {
                background: ${CONFIG.theme.border};
                cursor: not-allowed;
            }

            /* 响应式 */
            @media (max-width: 480px) {
                #aimed-bot-window {
                    width: calc(100vw - 48px);
                    height: calc(100vh - 160px);
                    right: 24px;
                    left: auto;
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(container);
    }

    // ============================================
    // 工具函数
    // ============================================
    function getTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ============================================
    // 核心功能
    // ============================================
    function toggle() {
        isOpen = !isOpen;
        const window = document.getElementById('aimed-bot-window');
        const badge = document.querySelector('.aimed-bot-badge');
        
        if (isOpen) {
            window.classList.add('show');
            if (badge) badge.style.display = 'none';
            document.getElementById('aimed-bot-input').focus();
        } else {
            window.classList.remove('show');
        }
    }

    function send() {
        const input = document.getElementById('aimed-bot-input');
        const text = input.value.trim();
        if (!text || isTyping) return;

        // 添加用户消息
        addMessage(text, 'user');
        input.value = '';

        // 隐藏快捷问题
        document.getElementById('aimed-bot-quick').style.display = 'none';

        // 显示打字指示器
        showTyping();

        // 调用 API
        callChatAPI(text);
    }

    function sendQuick(text) {
        document.getElementById('aimed-bot-input').value = text;
        send();
    }

    function addMessage(text, role) {
        const messages = document.getElementById('aimed-bot-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `aimed-bot-message ${role}`;
        
        const avatar = role === 'bot' ? '🤖' : '👤';
        const content = role === 'bot' ? text.replace(/\n/g, '<br>') : escapeHtml(text);
        
        msgDiv.innerHTML = `
            <div class="aimed-bot-msg-avatar">${avatar}</div>
            <div class="aimed-bot-msg-content">
                <div class="aimed-bot-msg-text">${content}</div>
                <div class="aimed-bot-msg-time">${getTime()}</div>
            </div>
        `;
        
        messages.appendChild(msgDiv);
        messages.scrollTop = messages.scrollHeight;

        // 保存历史
        conversationHistory.push({ role, content: text });
    }

    function showTyping() {
        isTyping = true;
        const messages = document.getElementById('aimed-bot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'aimed-bot-message bot';
        typingDiv.id = 'aimed-bot-typing-indicator';
        typingDiv.innerHTML = `
            <div class="aimed-bot-msg-avatar">🤖</div>
            <div class="aimed-bot-msg-content">
                <div class="aimed-bot-typing">
                    <div class="aimed-bot-typing-dot"></div>
                    <div class="aimed-bot-typing-dot"></div>
                    <div class="aimed-bot-typing-dot"></div>
                </div>
            </div>
        `;
        messages.appendChild(typingDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    function hideTyping() {
        isTyping = false;
        const typing = document.getElementById('aimed-bot-typing-indicator');
        if (typing) typing.remove();
    }

    function handleKey(event) {
        if (event.key === 'Enter') {
            send();
        }
    }

    async function callChatAPI(text) {
        try {
            const token = localStorage.getItem('jwt_token');
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = 'Bearer ' + token;

            const res = await fetch(CONFIG.apiEndpoint, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    message: text,
                    history: conversationHistory.slice(-10), // 保留最近 10 轮对话
                    model: 'dashscope/qwen3.5-plus',
                }),
            });

            if (!res.ok) throw new Error('请求失败');

            const data = await res.json();
            hideTyping();

            if (data.reply) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage('超人暂时无法回复，请稍后再试 😅', 'bot');
            }
        } catch (err) {
            hideTyping();
            console.error('AIMED 超人 API 调用失败:', err);
            addMessage('网络开小差了，请稍后再试 😅', 'bot');
        }
    }

    // ============================================
    // 公开 API
    // ============================================
    window.AIMEDBot = {
        toggle,
        send,
        sendQuick,
        handleKey,
        isOpen: () => isOpen,
        getHistory: () => conversationHistory,
        clearHistory: () => {
            conversationHistory = [];
            document.getElementById('aimed-bot-messages').innerHTML = '';
        },
    };

    // ============================================
    // 初始化
    // ============================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createBotUI);
    } else {
        createBotUI();
    }

})();
