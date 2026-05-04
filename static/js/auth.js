/**
 * 统一登录状态检测
 * 自动检测登录状态，更新导航栏显示
 */

(function() {
    'use strict';

    // 检测当前平台
    function detectPlatform() {
        const path = window.location.pathname;
        if (path.startsWith('/service/')) return 'service';
        if (path.startsWith('/admin/')) return 'admin';
        return null;
    }

    // 检查登录状态
    function checkLoginStatus() {
        const platform = detectPlatform();
        if (!platform) return null;

        const key = platform === 'service' ? 'loginStatus' : 'adminLogin';
        const loginStatus = localStorage.getItem(key);
        if (!loginStatus) return null;
        
        try {
            const data = JSON.parse(loginStatus);
            // 检查是否过期（24 小时）
            if (Date.now() - new Date(data.timestamp).getTime() > 24*60*60*1000) {
                localStorage.removeItem(key);
                return null;
            }
            return { data, key, platform };
        } catch(e) {
            return null;
        }
    }

    // 更新导航栏登录状态
    function updateNavLogin() {
        const loginInfo = checkLoginStatus();
        const loginLink = document.getElementById('loginLink');
        
        if (!loginLink) return;

        if (loginInfo) {
            const { data, key, platform } = loginInfo;
            const userName = data.username || data.identityId || '用户';
            
            loginLink.innerHTML = `👤 ${userName}`;
            loginLink.className = 'nav-user';
            loginLink.href = '#';
            loginLink.onclick = function(e) {
                e.preventDefault();
                if (confirm('确定要退出登录吗？')) {
                    localStorage.removeItem(key);
                    const redirect = platform === 'service' ? '/service/login.html' : '/admin/index.html';
                    window.location.href = redirect;
                }
            };
        } else {
            const platform = detectPlatform();
            const loginHref = platform === 'service' ? '/service/login.html' : '/admin/index.html';
            loginLink.innerHTML = '登录';
            loginLink.className = 'nav-login';
            loginLink.href = loginHref;
            loginLink.onclick = null;
        }
    }

    // 页面加载后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateNavLogin);
    } else {
        updateNavLogin();
    }

})();
