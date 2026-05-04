/**
 * ShieldOps - Login & Registration Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            const sunIcon = document.querySelector('.sun-icon');
            const moonIcon = document.querySelector('.moon-icon');
            if (sunIcon) sunIcon.style.display = 'none';
            if (moonIcon) moonIcon.style.display = 'block';
        }
        
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            const sunIcon = document.querySelector('.sun-icon');
            const moonIcon = document.querySelector('.moon-icon');
            if (sunIcon) sunIcon.style.display = isDark ? 'none' : 'block';
            if (moonIcon) moonIcon.style.display = isDark ? 'block' : 'none';
        });
    }

    // Login and Register Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('.login-btn');
            const isRegistering = btn.innerText === 'Register';
            const endpoint = isRegistering ? '/register' : '/login';
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value
                    })
                });
                
                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const data = await response.json();
                    showNotification('Error', data.error || 'Authentication failed', 'danger');
                }
            } catch (err) {
                showNotification('Error', 'Connection failed. Please try again.', 'danger');
            }
        });

        // Add toggle link
        const toggleLink = document.createElement('p');
        toggleLink.id = 'toggle-auth';
        toggleLink.style.cssText = 'text-align:center; cursor:pointer; color:var(--primary); font-size:14px; margin-top:10px;';
        toggleLink.textContent = 'Need an account? Register here.';
        loginForm.appendChild(toggleLink);

        toggleLink.addEventListener('click', (e) => {
            const btn = loginForm.querySelector('.login-btn');
            if(btn.innerText === 'Login') {
                btn.innerText = 'Register';
                e.target.textContent = 'Already have an account? Login here.';
            } else {
                btn.innerText = 'Login';
                e.target.textContent = 'Need an account? Register here.';
            }
        });
    }

    // SOS button
    const sosButton = document.getElementById('sosButton');
    if (sosButton) {
        sosButton.addEventListener('click', () => {
            sosButton.classList.add('sos-active');
            sosButton.innerHTML = ''; // Clear
            
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'sos-icon sos-pulse');
            svg.setAttribute('viewBox', '0 0 24 24');
            svg.setAttribute('fill', 'none');
            svg.setAttribute('stroke', 'currentColor');
            svg.setAttribute('stroke-width', '2');
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', 'M22 12h-4l-3 9L9 3l-3 9H2');
            svg.appendChild(path);
            
            const text = document.createElement('span');
            text.textContent = 'Deploying Help...';
            
            sosButton.appendChild(svg);
            sosButton.appendChild(text);
            
            showNotification('SOS Alert', 'Emergency help is being deployed to your location. Stay safe!', 'warning');
            
            setTimeout(() => {
                sosButton.classList.remove('sos-active');
                sosButton.innerHTML = `
                    <svg class="sos-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>SOS - Emergency Help</span>
                `;
            }, 3000);
        });
    }
});

// Notification function
function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: var(--bg-primary);
        border: 1px solid var(--border);
        border-left: 4px solid var(--${type === 'warning' ? 'warning' : 'danger'});
        border-radius: var(--radius);
        padding: 16px;
        box-shadow: var(--shadow-lg);
        max-width: 400px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = 'display: flex; justify-content: space-between; align-items: start; gap: 12px;';
    
    const textContent = document.createElement('div');
    const titleStrong = document.createElement('strong');
    titleStrong.style.cssText = 'display: block; margin-bottom: 4px; color: var(--text-primary);';
    titleStrong.textContent = title;
    
    const messageP = document.createElement('p');
    messageP.style.cssText = 'margin: 0; color: var(--text-secondary); font-size: 14px;';
    messageP.textContent = message;
    
    textContent.appendChild(titleStrong);
    textContent.appendChild(messageP);
    
    const closeBtn = document.createElement('button');
    closeBtn.style.cssText = 'background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 20px; padding: 0; line-height: 1;';
    closeBtn.textContent = '×';
    closeBtn.onclick = () => notification.remove();
    
    content.appendChild(textContent);
    content.appendChild(closeBtn);
    notification.appendChild(content);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}
