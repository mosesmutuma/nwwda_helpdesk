document.addEventListener("DOMContentLoaded", function () {
    const applyStats = () => {
        // 1. Get the numbers from the hidden bridge
        const bridge = document.querySelector('#stat-bridge');
        if (!bridge) return;

        // Extract numbers (Jazzmin puts the value in the attribute)
        const stats = {
            'Pending': bridge.getAttribute('data-p') || "0",
            'In Progress': bridge.getAttribute('data-ip') || "0",
            'Resolved': bridge.getAttribute('data-r') || "0"
        };

        // 2. Find the colored buttons and inject the numbers
        document.querySelectorAll('.nav-link').forEach(link => {
            const text = link.textContent.trim();
            
            Object.keys(stats).forEach(key => {
                if (text.includes(key)) {
                    let badge = link.querySelector('.badge');
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.className = 'badge badge-pill ml-2';
                        badge.style.background = 'rgba(0,0,0,0.3)';
                        link.appendChild(badge);
                    }
                    badge.textContent = stats[key];
                    
                    // Pulse Pending if > 0
                    if (key === 'Pending' && parseInt(stats[key]) > 0) {
                        link.style.animation = "rapid-pulse 0.8s infinite ease-in-out";
                    }
                }
            });
        });
    };

    // Run once, then again after 1 second to beat the Jazzmin cache
    applyStats();
    setTimeout(applyStats, 1000);
});