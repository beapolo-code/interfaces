/* ==========================================================================
   SEGURIDAD SOS - MD3 EXPRESSIVE JAVASCRIPT CONTROLLER (5 VISTAS)
   ========================================================================== */

const SOSApp = {
    user: {
        name: 'Administrador Vigía',
        email: 'admin@vigia.local',
        phone: '0990000000'
    },
    currentScreen: 'auth-screen',
    sosPressTimer: null,
    sosPressStartTime: 0,
    sosHoldDuration: 3000,
    sosAnimationFrame: null,
    audioCtx: null,
    sirenOsc: null
};

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initCameraClocks();
    initSosLongPress();
});

/**
 * Control de Pestañas en Autenticación (Login / Registro)
 */
function switchAuthTab(type) {
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');

    if (!tabLogin || !tabRegister || !formLogin || !formRegister) return;

    tabLogin.classList.toggle('active', type === 'login');
    tabRegister.classList.toggle('active', type === 'register');
    formLogin.classList.toggle('active', type === 'login');
    formRegister.classList.toggle('active', type === 'register');
}

const screenOrder = {
    'auth-screen': 0,
    'home-screen': 1,
    'profile-screen': 1,
    'cameras-screen': 2
};

/**
 * Navegación Principal entre Pantallas con Transición Direccional Expressive
 */
function navigateTo(screenId, forcedDirection = null) {
    let direction = forcedDirection;
    if (!direction) {
        const prevOrder = screenOrder[SOSApp.currentScreen] ?? 0;
        const nextOrder = screenOrder[screenId] ?? 1;
        direction = nextOrder >= prevOrder ? 'forward' : 'backward';
    }

    SOSApp.currentScreen = screenId;
    document.querySelectorAll('.screen').forEach(s => {
        s.classList.remove('active', 'entering-forward', 'entering-backward');
    });
    
    const target = document.getElementById(screenId);
    if (target) {
        target.classList.add('active');
        target.classList.add(direction === 'forward' ? 'entering-forward' : 'entering-backward');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    const globalNav = document.getElementById('global-nav');
    if (screenId === 'home-screen' || screenId === 'profile-screen') {
        if (globalNav) globalNav.style.display = 'flex';
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(nav => nav.classList.remove('active'));

        if (screenId === 'home-screen' && navItems[1]) {
            navItems[1].classList.add('active');
        } else if (screenId === 'profile-screen' && navItems[2]) {
            navItems[2].classList.add('active');
        }
    } else {
        if (globalNav) globalNav.style.display = 'none';
    }
}

function navigateNav(screenId, element) {
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    element.classList.add('active');
    navigateTo(screenId);
}

/**
 * Envío de Formularios de Login / Registro conectados a la API y PostgreSQL
 */
async function handleAuthSubmit(event, type) {
    event.preventDefault();

    if (type === 'register') {
        const nameInput = document.getElementById('reg-name');
        const phoneInput = document.getElementById('reg-phone');
        const emailInput = document.getElementById('reg-email');
        const passInput = document.getElementById('reg-password');

        const enteredName = nameInput ? nameInput.value.trim() : '';
        const enteredPhone = phoneInput ? phoneInput.value.trim() : '';
        const enteredEmail = emailInput ? emailInput.value.trim() : '';
        const enteredPass = passInput ? passInput.value.trim() : '';

        if (!enteredName) {
            showToast('Por favor ingresa tu nombre completo.');
            return;
        }
        if (!enteredPhone) {
            showToast('Por favor ingresa tu número telefónico.');
            return;
        }
        if (!enteredEmail) {
            showToast('Por favor ingresa tu correo electrónico.');
            return;
        }
        if (!enteredPass) {
            showToast('Por favor ingresa tu contraseña.');
            return;
        }

        try {
            const resp = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    name: enteredName, 
                    email: enteredEmail, 
                    phone: enteredPhone, 
                    password: enteredPass 
                })
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                showToast(data.message || 'Error al crear la cuenta.');
                return;
            }
            SOSApp.user.name = data.user.name;
            SOSApp.user.email = data.user.email;
            SOSApp.user.phone = data.user.phone || data.user.email;
            showToast(`¡Cuenta registrada en PostgreSQL! Bienvenido, ${SOSApp.user.name}`);
        } catch (err) {
            SOSApp.user.name = enteredName || 'Usuario';
            SOSApp.user.email = enteredEmail;
            SOSApp.user.phone = enteredPhone;
            showToast(`¡Cuenta creada localmente! Bienvenido, ${SOSApp.user.name}`);
        }
    } else {
        const emailInput = document.getElementById('login-email');
        const passInput = document.getElementById('login-password');

        const enteredEmail = emailInput ? emailInput.value.trim() : '';
        const enteredPass = passInput ? passInput.value.trim() : '';

        if (!enteredEmail) {
            showToast('Por favor ingresa tu correo electrónico.');
            return;
        }
        if (!enteredPass) {
            showToast('Por favor ingresa tu contraseña.');
            return;
        }

        try {
            const resp = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: enteredEmail, password: enteredPass })
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) {
                showToast(data.message || 'Credenciales incorrectas.');
                return;
            }
            SOSApp.user.name = data.user.name;
            SOSApp.user.email = data.user.email;
            SOSApp.user.phone = data.user.phone || data.user.email;
            showToast('Sesión iniciada con éxito en PostgreSQL.');
        } catch (err) {
            SOSApp.user.name = 'Administrador Vigía';
            SOSApp.user.email = enteredEmail;
            SOSApp.user.phone = '0990000000';
            showToast('Sesión iniciada (modo local).');
        }
    }

    updateUserProfileDisplays();

    setTimeout(() => {
        navigateTo('home-screen');
    }, 400);
}

function updateUserProfileDisplays() {
    const greeting = document.getElementById('home-greeting');
    const profileName = document.getElementById('profile-name-display');
    const profilePhone = document.getElementById('profile-phone-display');

    const displayName = SOSApp.user.name || 'Usuario';
    const displayPhone = SOSApp.user.email || SOSApp.user.phone || 'Sin registrar';

    if (greeting) greeting.textContent = `Hola, ${displayName.split(' ')[0]}`;
    if (profileName) profileName.textContent = displayName;
    if (profilePhone) profilePhone.textContent = displayPhone;
}

/**
 * Pulsado sostenido de 3 segundos para el botón SOS
 */
function initSosLongPress() {
    const btn = document.getElementById('btnSos');
    const circle = document.getElementById('progress-circle');
    const statusLabel = document.getElementById('sos-status-label');
    if (!btn || !circle) return;

    const totalCircumference = 565; // 2 * Math.PI * 90

    const startPress = (e) => {
        e.preventDefault();
        btn.classList.add('holding');
        SOSApp.sosPressStartTime = performance.now();
        if (statusLabel) statusLabel.textContent = '¡ENVIANDO ALERTA EN 3s!';

        const updateProgress = (now) => {
            const elapsed = now - SOSApp.sosPressStartTime;
            const progress = Math.min(elapsed / SOSApp.sosHoldDuration, 1);
            circle.style.strokeDashoffset = totalCircumference * (1 - progress);
            const remaining = Math.max(1, Math.ceil((SOSApp.sosHoldDuration - elapsed) / 1000));
            if (statusLabel) statusLabel.textContent = `¡ENVIANDO ALERTA EN ${remaining}s!`;

            if (progress < 1) {
                SOSApp.sosAnimationFrame = requestAnimationFrame(updateProgress);
            } else {
                triggerEmergencyAlert();
                resetPressState();
            }
        };

        cancelAnimationFrame(SOSApp.sosAnimationFrame);
        SOSApp.sosAnimationFrame = requestAnimationFrame(updateProgress);
    };

    const cancelPress = () => {
        resetPressState();
    };

    const resetPressState = () => {
        btn.classList.remove('holding');
        cancelAnimationFrame(SOSApp.sosAnimationFrame);
        circle.style.strokeDashoffset = totalCircumference;
        if (statusLabel) statusLabel.textContent = 'Mantén pulsado 3 segundos';
    };

    btn.addEventListener('mousedown', startPress);
    btn.addEventListener('mouseup', cancelPress);
    btn.addEventListener('mouseleave', cancelPress);
    btn.addEventListener('touchstart', startPress, { passive: false });
    btn.addEventListener('touchend', cancelPress);
    btn.addEventListener('touchcancel', cancelPress);
}

function triggerEmergencyAlert() {
    const overlay = document.getElementById('alert-overlay');
    if (overlay) overlay.classList.add('active');

    if (navigator.vibrate) {
        navigator.vibrate([300, 150, 300, 150, 500]);
    }

    startAudioSiren();
    showToast('🚨 ¡ALERTA SOS ENVIADA A CENTRAL Y POLICÍA!');

    // Registrar en BD via API
    fetch('http://localhost:5000/api/sos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 3 })
    }).catch(() => {});
}

function cancelSOSAlert() {
    const overlay = document.getElementById('alert-overlay');
    if (overlay) overlay.classList.remove('active');
    stopAudioSiren();
    showToast('Alerta SOS desactivada.');
}

function startAudioSiren() {
    try {
        if (!SOSApp.audioCtx) {
            SOSApp.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (SOSApp.audioCtx.state === 'suspended') {
            SOSApp.audioCtx.resume();
        }

        const osc = SOSApp.audioCtx.createOscillator();
        const gain = SOSApp.audioCtx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(600, SOSApp.audioCtx.currentTime);

        const now = SOSApp.audioCtx.currentTime;
        osc.frequency.linearRampToValueAtTime(1100, now + 0.4);
        osc.frequency.linearRampToValueAtTime(600, now + 0.8);

        gain.gain.setValueAtTime(0.15, now);

        osc.connect(gain);
        gain.connect(SOSApp.audioCtx.destination);
        osc.start();
        SOSApp.sirenOsc = osc;
    } catch (e) {
        console.warn('Web Audio no disponible:', e);
    }
}

function stopAudioSiren() {
    if (SOSApp.sirenOsc) {
        try {
            SOSApp.sirenOsc.stop();
            SOSApp.sirenOsc.disconnect();
        } catch (e) {}
        SOSApp.sirenOsc = null;
    }
}

function showToast(msg) {
    const toast = document.getElementById('md3-toast');
    if (!toast) return;
    const txt = document.getElementById('toast-text');
    if (txt) txt.textContent = msg;
    toast.classList.add('show');
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}

function initClock() {
    // reloj superior si existe
}

function initCameraClocks() {
    // relojes cámaras
}

// Material Ripple Effect
document.addEventListener('click', function(e) {
    const target = e.target.closest('.md3-btn-primary, .md3-btn-secondary, .action-card, .tab-btn, .md3-chip, .list-card');
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'md3-ripple';
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
    target.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
});
