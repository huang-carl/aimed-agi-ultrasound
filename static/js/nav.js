/**
 * 统一导航栏组件
 * 自动检测登录状态，显示用户信息或登录按钮
 */

(function() {
    'use strict';

    // 导航栏配置
    const NAV_CONFIG = {
        service: {
            title: '联合实验室',
            logo: '../aimed-logo-new.jpg',
            links: [
                { text: '官网', href: '/' },
                { text: '管理平台', href: '/admin/' }
            ],
            loginHref: '/service/login.html',
            logoutHref: '/service/login.html'
        },
        admin: {
            title: '管理平台',
            logo: '../aimed-logo-new.jpg',
            links: [
                { text: '官网', href: '/' },
                { text: '服务平台', href: '/service/' }
            ],
            loginHref: '/admin/index.html',
            logoutHref: '/admin/index.html'
        }
    };

    // 检测当前平台
    function detectPlatform() {
        const path = window.location.pathname;
        if (path.startsWith('/service/')) return 'service';
        if (path.startsWith('/admin/')) return 'admin';
        return null;
    }

    // 检查登录状态
    function checkLoginStatus(platform) {
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
            return data;
        } catch(e) {
            return null;
        }
    }

    // 退出登录
    function logout(platform) {
        if (!confirm('确定要退出登录吗？')) return;
        const key = platform === 'service' ? 'loginStatus' : 'adminLogin';
        localStorage.removeItem(key);
        window.location.href = platform === 'service' ? '/service/login.html' : '/admin/index.html';
    }

    // 创建导航栏 HTML
    function createNavbar(platform) {
        const config = NAV_CONFIG[platform];
        if (!config) return '';

        const loginData = checkLoginStatus(platform);
        const isLoggedIn = !!loginData;
        const userName = loginData ? (loginData.username || loginData.identityId || '用户') : '';

        let loginButton = '';
        if (isLoggedIn) {
            loginButton = `
                <a href="#" class="nav-user" onclick="window.NAV.logout('${platform}'); return false;">
                    👤 ${userName}
                </a>
            `;
        } else {
            loginButton = `
                <a href="${config.loginHref}" class="nav-login">登录</a>
            `;
        }

        let linksHtml = config.links.map(link => 
            `<li><a href="${link.href}">${link.text}</a></li>`
        ).join('');

        return `
            <nav class="navbar">
                <div class="nav-container">
                    <a href="/" class="logo">
                        <img src="${config.logo}" alt="AIMED">
                        <span>${config.title}</span>
                    </a>
                    <ul class="nav-links">
                        ${linksHtml}
                        <li>${loginButton}</li>
                    </ul>
                </div>
            </nav>
        `;
    }

    // 注入导航栏
    function injectNavbar() {
        const platform = detectPlatform();
        if (!platform) return;

        const navbarHtml = createNavbar(platform);
        const navContainer = document.querySelector('.nav-container');
        if (navContainer) {
            navContainer.innerHTML = navbarHtml;
        } else {
            // 如果没有 .nav-container，则替换整个 nav
            const nav = document.querySelector('nav');
            if (nav) {
                nav.outerHTML = navbarHtml;
            }
        }
    }

    // 暴露全局 API
    window.NAV = {
        logout: logout,
        checkLoginStatus: checkLoginStatus,
        detectPlatform: detectPlatform
    };

    // 页面加载后自动注入
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectNavbar);
    } else {
        injectNavbar();
    }

})();
