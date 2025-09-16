// تطبيق الشات بوت التعليمي
class EducationalChatbot {
    constructor() {
        this.apiBase = '';  // سيستخدم نفس النطاق
        this.currentSession = null;
        this.currentDomain = null;
        this.selectedDomainId = null;
        this.availableDomains = [];
        this.isConnected = false;
        this.settings = this.loadSettings();

        this.initializeElements();
        this.bindEvents();
        this.checkConnection();
        this.loadDomains();
        this.applySettings();
    }

    // تحميل الإعدادات من localStorage
    loadSettings() {
        const defaultSettings = {
            fontSize: '16',
            theme: 'light',
            autoScroll: true
        };

        const savedSettings = localStorage.getItem('chatbot_settings');
        return savedSettings ? {...defaultSettings, ...JSON.parse(savedSettings)} : defaultSettings;
    }

    // حفظ الإعدادات
    saveSettings() {
        localStorage.setItem('chatbot_settings', JSON.stringify(this.settings));
    }

    // تطبيق الإعدادات
    applySettings() {
        // تطبيق حجم الخط
        document.documentElement.style.setProperty('--base-font-size', this.settings.fontSize + 'px');

        // تطبيق السمة
        if (this.settings.theme === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        // تحديث عناصر الإعدادات في Modal
        if (this.elements.fontSizeSelect) {
            this.elements.fontSizeSelect.value = this.settings.fontSize;
        }
        if (this.elements.themeSelect) {
            this.elements.themeSelect.value = this.settings.theme;
        }
        if (this.elements.autoScrollCheck) {
            this.elements.autoScrollCheck.checked = this.settings.autoScroll;
        }
    }

    // تهيئة العناصر
    initializeElements() {
        this.elements = {
            // صفحة اختيار التخصص
            domainSelection: document.getElementById('domainSelection'),
            domainsGrid: document.getElementById('domainsGrid'),
            startChatBtn: document.getElementById('startChatBtn'),

            // واجهة الشات
            chatInterface: document.getElementById('chatInterface'),
            domainName: document.getElementById('domainName'),
            domainDescription: document.getElementById('domainDescription'),
            messagesContainer: document.getElementById('messagesContainer'),
            welcomeText: document.getElementById('welcomeText'),

            // منطقة الإدخال
            messageForm: document.getElementById('messageForm'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            charCounter: document.getElementById('charCounter'),

            // مؤشر الكتابة والحالة
            typingIndicator: document.getElementById('typingIndicator'),
            connectionStatus: document.getElementById('connectionStatus'),

            // أزرار الإجراءات
            newChatBtn: document.getElementById('newChatBtn'),
            historyBtn: document.getElementById('historyBtn'),
            settingsBtn: document.getElementById('settingsBtn'),

            // النوافذ المنبثقة
            historyModal: document.getElementById('historyModal'),
            settingsModal: document.getElementById('settingsModal'),
            closeHistoryModal: document.getElementById('closeHistoryModal'),
            closeSettingsModal: document.getElementById('closeSettingsModal'),
            historyContent: document.getElementById('historyContent'),

            // عناصر الإعدادات
            fontSizeSelect: document.getElementById('fontSize'),
            themeSelect: document.getElementById('theme'),
            autoScrollCheck: document.getElementById('autoScroll')
        };
    }

    // ربط الأحداث
    bindEvents() {
        // بدء المحادثة
        this.elements.startChatBtn.addEventListener('click', () => this.startChat());

        // إرسال الرسالة
        this.elements.messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // مراقبة تغيير النص
        this.elements.messageInput.addEventListener('input', () => {
            this.updateCharCounter();
            this.autoResizeTextarea();
        });

        // إرسال بـ Enter (مع Shift للسطر الجديد)
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // أزرار الإجراءات
        this.elements.newChatBtn.addEventListener('click', () => this.startNewChat());
        this.elements.historyBtn.addEventListener('click', () => this.showHistory());
        this.elements.settingsBtn.addEventListener('click', () => this.showSettings());

        // إغلاق النوافذ المنبثقة
        this.elements.closeHistoryModal.addEventListener('click', () => this.hideModal('historyModal'));
        this.elements.closeSettingsModal.addEventListener('click', () => this.hideModal('settingsModal'));

        // إغلاق النوافذ بالنقر خارجها
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal(e.target.id);
            }
        });

        // مراقبة تغييرات الإعدادات
        if (this.elements.fontSizeSelect) {
            this.elements.fontSizeSelect.addEventListener('change', (e) => {
                this.settings.fontSize = e.target.value;
                this.saveSettings();
                this.applySettings();
            });
        }

        if (this.elements.themeSelect) {
            this.elements.themeSelect.addEventListener('change', (e) => {
                this.settings.theme = e.target.value;
                this.saveSettings();
                this.applySettings();
            });
        }

        if (this.elements.autoScrollCheck) {
            this.elements.autoScrollCheck.addEventListener('change', (e) => {
                this.settings.autoScroll = e.target.checked;
                this.saveSettings();
            });
        }
    }

    // فحص الاتصال
    async checkConnection() {
        try {
            this.updateConnectionStatus('connecting', 'جاري الاتصال...');
            const response = await fetch(`${this.apiBase}/api/health`);
            const data = await response.json();

            if (data.status === 'healthy') {
                this.isConnected = true;
                this.updateConnectionStatus('connected', 'متصل');
            } else {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected', 'اتصال محدود');
            }
        } catch (error) {
            this.isConnected = false;
            this.updateConnectionStatus('disconnected', 'غير متصل');
            console.error('خطأ في فحص الاتصال:', error);
        }
    }

    // تحديث حالة الاتصال
    updateConnectionStatus(status, message) {
        this.elements.connectionStatus.className = `connection-status ${status}`;
        this.elements.connectionStatus.querySelector('span').textContent = message;
    }

    // تحميل التخصصات المتاحة
    async loadDomains() {
        try {
            const response = await fetch(`${this.apiBase}/api/domains`);
            const data = await response.json();
            this.availableDomains = data.domains;
            this.renderDomains();
        } catch (error) {
            console.error('خطأ في تحميل التخصصات:', error);
            this.showError('فشل في تحميل التخصصات المتاحة');
        }
    }

    // عرض التخصصات
    renderDomains() {
        this.elements.domainsGrid.innerHTML = '';

        this.availableDomains.forEach(domain => {
            const domainElement = document.createElement('div');
            domainElement.className = 'domain-option';
            domainElement.dataset.domainId = domain.domain_id;

            domainElement.innerHTML = `
                <h3>${domain.name}</h3>
                <p>${domain.description}</p>
            `;

            domainElement.addEventListener('click', () => {
                this.selectDomain(domain.domain_id, domain);
            });

            this.elements.domainsGrid.appendChild(domainElement);
        });
    }

    // اختيار التخصص
    selectDomain(domainId, domainData) {
        // إزالة التحديد من جميع الخيارات
        document.querySelectorAll('.domain-option').forEach(option => {
            option.classList.remove('selected');
        });

        // تحديد الخيار المختار
        document.querySelector(`[data-domain-id="${domainId}"]`).classList.add('selected');

        this.selectedDomainId = domainId;
        this.currentDomain = domainData;
        this.elements.startChatBtn.disabled = false;
    }

    // بدء المحادثة
    async startChat() {
        if (!this.selectedDomainId) {
            this.showError('يرجى اختيار التخصص أولاً');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/chat/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    domain: this.selectedDomainId
                })
            });

            const data = await response.json();
            this.currentSession = data.session_id;

            // تحديث واجهة الشات
            this.elements.domainName.textContent = this.currentDomain.name;
            this.elements.domainDescription.textContent = this.currentDomain.description;
            this.elements.welcomeText.textContent = data.message;

            // التبديل إلى واجهة الشات
            this.elements.domainSelection.style.display = 'none';
            this.elements.chatInterface.style.display = 'flex';

            // تركيز حقل الإدخال
            this.elements.messageInput.focus();

        } catch (error) {
            console.error('خطأ في بدء المحادثة:', error);
            this.showError('فشل في بدء المحادثة');
        }
    }

    // بدء محادثة جديدة
    async startNewChat() {
        if (confirm('هل تريد بدء محادثة جديدة؟ سيتم حذف المحادثة الحالية.')) {
            // مسح الرسائل
            this.elements.messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="bot-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <p id="welcomeText">مرحباً! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟</p>
                    </div>
                </div>
            `;

            // إنشاء جلسة جديدة
            await this.startChat();
        }
    }

    // إرسال الرسالة
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || !this.currentSession) return;

        // تعطيل زر الإرسال
        this.elements.sendBtn.disabled = true;
        this.elements.messageInput.disabled = true;

        try {
            // إضافة رسالة المستخدم
            this.addMessage('user', message);

            // مسح حقل الإدخال
            this.elements.messageInput.value = '';
            this.updateCharCounter();

            // عرض مؤشر الكتابة
            this.showTypingIndicator();

            // إرسال الرسالة إلى الخادم
            const response = await fetch(`${this.apiBase}/api/chat/${this.currentSession}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    domain: this.selectedDomainId
                })
            });

            const data = await response.json();

            // إخفاء مؤشر الكتابة
            this.hideTypingIndicator();

            // إضافة رد المساعد
            this.addMessage('assistant', data.message);

        } catch (error) {
            this.hideTypingIndicator();
            console.error('خطأ في إرسال الرسالة:', error);
            this.showError('فشل في إرسال الرسالة');
        } finally {
            // إعادة تفعيل الإدخال
            this.elements.sendBtn.disabled = false;
            this.elements.messageInput.disabled = false;
            this.elements.messageInput.focus();
        }
    }

    // إضافة رسالة إلى المحادثة
    addMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role} fade-in`;

        const avatar = role === 'user' ? 
            '<div class="message-avatar user-avatar"><i class="fas fa-user"></i></div>' :
            '<div class="message-avatar bot-avatar"><i class="fas fa-robot"></i></div>';

        messageElement.innerHTML = `
            ${avatar}
            <div class="message-content">
                <p>${this.formatMessage(content)}</p>
            </div>
        `;

        this.elements.messagesContainer.appendChild(messageElement);

        if (this.settings.autoScroll) {
            this.scrollToBottom();
        }
    }

    // تنسيق الرسالة
    formatMessage(content) {
        // تحويل أكواد إلى blocks
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // تحويل الأكواد المضمنة
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');

        // تحويل الروابط
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

        // تحويل أسطر جديدة
        content = content.replace(/\n/g, '<br>');

        return content;
    }

    // التمرير إلى الأسفل
    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    }

    // عرض مؤشر الكتابة
    showTypingIndicator() {
        this.elements.typingIndicator.style.display = 'flex';
        if (this.settings.autoScroll) {
            this.scrollToBottom();
        }
    }

    // إخفاء مؤشر الكتابة
    hideTypingIndicator() {
        this.elements.typingIndicator.style.display = 'none';
    }

    // تحديث عداد الأحرف
    updateCharCounter() {
        const length = this.elements.messageInput.value.length;
        this.elements.charCounter.textContent = length;

        if (length > 800) {
            this.elements.charCounter.style.color = 'var(--warning-color)';
        } else if (length > 950) {
            this.elements.charCounter.style.color = 'var(--danger-color)';
        } else {
            this.elements.charCounter.style.color = 'var(--text-light)';
        }
    }

    // تعديل حجم منطقة النص تلقائياً
    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    // عرض التاريخ
    async showHistory() {
        if (!this.currentSession) {
            this.showError('لا توجد محادثة نشطة');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/chat/${this.currentSession}/history`);
            const data = await response.json();

            let historyHTML = '';
            data.messages.forEach(msg => {
                const time = new Date(msg.timestamp).toLocaleString('ar');
                const role = msg.role === 'user' ? 'أنت' : 'المساعد';

                historyHTML += `
                    <div class="history-message">
                        <div class="history-header">
                            <strong>${role}</strong>
                            <span class="history-time">${time}</span>
                        </div>
                        <div class="history-content">${this.formatMessage(msg.content)}</div>
                    </div>
                `;
            });

            this.elements.historyContent.innerHTML = historyHTML || '<p>لا توجد رسائل في التاريخ</p>';
            this.showModal('historyModal');

        } catch (error) {
            console.error('خطأ في تحميل التاريخ:', error);
            this.showError('فشل في تحميل تاريخ المحادثة');
        }
    }

    // عرض الإعدادات
    showSettings() {
        this.showModal('settingsModal');
    }

    // عرض النافذة المنبثقة
    showModal(modalId) {
        document.getElementById(modalId).classList.add('show');
    }

    // إخفاء النافذة المنبثقة
    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    }

    // عرض رسالة خطأ
    showError(message) {
        // يمكن تطوير هذا لعرض toast notification
        alert(message);
    }
}

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new EducationalChatbot();
});

// إضافة أنماط CSS للتاريخ
const historyStyles = `
<style>
.history-message {
    margin-bottom: 1rem;
    padding: 1rem;
    border-radius: 8px;
    background: var(--bg-light);
}

.history-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

.history-time {
    color: var(--text-light);
}

.history-content {
    line-height: 1.5;
}

.history-content code {
    background: rgba(37, 99, 235, 0.1);
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
}

.history-content pre {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
    margin: 0.5rem 0;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', historyStyles);