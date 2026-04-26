/**
 * Portal 通用登录检查脚本
 * 所有 Portal 页面引入此脚本即可自动检查登录状态
 */

(function() {
    // 检查登录状态
    function checkLogin() {
        const loginStatus = localStorage.getItem('loginStatus');
        if (!loginStatus) {
            // 未登录，跳转到登录页
            window.location.href = '/portal/login.html?redirect=' + encodeURIComponent(window.location.pathname);
            return false;
        }
        
        try {
            const data = JSON.parse(loginStatus);
            const loginTime = new Date(data.timestamp).getTime();
            const now = Date.now();
            
            // 检查是否过期（24 小时）
            if (now - loginTime > 24 * 60 * 60 * 1000) {
                localStorage.removeItem('loginStatus');
                window.location.href = '/portal/login.html?redirect=' + encodeURIComponent(window.location.pathname);
                return false;
            }
            
            return data;
        } catch (e) {
            localStorage.removeItem('loginStatus');
            window.location.href = '/portal/login.html?redirect=' + encodeURIComponent(window.location.pathname);
            return false;
        }
    }
    
    // 退出登录
    function logout() {
        localStorage.removeItem('loginStatus');
        window.location.href = '/portal/login.html';
    }
    
    // 获取登录用户信息
    function getUserInfo() {
        const loginStatus = localStorage.getItem('loginStatus');
        if (!loginStatus) return null;
        try {
            return JSON.parse(loginStatus);
        } catch (e) {
            return null;
        }
    }
    
    // 更新导航栏用户信息
    function updateUserDisplay() {
        const user = getUserInfo();
        if (!user) return;
        
        const userName = user.username || user.identityId || '用户';
        const roleLabel = user.roleLabel || '';
        
        // 查找并更新用户名显示元素
        const userNameEl = document.querySelector('.user-name');
        if (userNameEl) {
            userNameEl.textContent = userName;
        }
        
        // 查找并更新角色显示元素
        const userRoleEl = document.querySelector('.user-role');
        if (userRoleEl) {
            userRoleEl.textContent = roleLabel;
        }
        
        // 查找并更新退出按钮
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('确定要退出登录吗？')) {
                    logout();
                }
            });
        }
    }
    
    // 暴露全局方法
    window.PortalAuth = {
        checkLogin: checkLogin,
        logout: logout,
        getUserInfo: getUserInfo,
        updateUserDisplay: updateUserDisplay
    };
})();
