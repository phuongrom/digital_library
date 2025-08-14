document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    initAnimations();
    initSearchEnhancement();
    initCardInteractions();
    initFormValidation();
    initThemeToggle();
    initScrollEffects();
});

function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-fade-in, .animate-slide-up').forEach(el => {
        observer.observe(el);
    });

    document.querySelectorAll('.book-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

function initSearchEnhancement() {
    const searchInput = document.querySelector('input[name="q"]');
    if (!searchInput) return;

    let searchTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            hideSearchSuggestions();
            return;
        }

        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });

    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    suggestionsContainer.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: var(--radius);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        max-height: 300px;
        overflow-y: auto;
        display: none;
    `;

    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(suggestionsContainer);
}

function performSearch(query) {
    const suggestions = [
        'Harry Potter và Hòn đá Phù thủy',
        'Nhà Giả Kim',
        'Đắc Nhân Tâm',
        'Sapiens: Lược sử loài người'
    ].filter(book => book.toLowerCase().includes(query.toLowerCase()));

    showSearchSuggestions(suggestions);
}

function showSearchSuggestions(suggestions) {
    const container = document.querySelector('.search-suggestions');
    if (!container) return;

    if (suggestions.length === 0) {
        container.innerHTML = '<div class="p-3 text-muted">Không tìm thấy kết quả</div>';
    } else {
        container.innerHTML = suggestions.map(book => 
            `<div class="suggestion-item p-3 border-bottom" style="cursor: pointer; transition: background-color 0.2s;">
                <i class="bi bi-search me-2 text-muted"></i>${book}
             </div>`
        ).join('');

        container.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'var(--gray-100)';
            });
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'transparent';
            });
            item.addEventListener('click', function() {
                document.querySelector('input[name="q"]').value = this.textContent.replace('🔍', '').trim();
                hideSearchSuggestions();
                document.querySelector('form').submit();
            });
        });
    }

    container.style.display = 'block';
}

function hideSearchSuggestions() {
    const container = document.querySelector('.search-suggestions');
    if (container) {
        container.style.display = 'none';
    }
}

function initCardInteractions() {
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = 'var(--shadow-xl)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow)';
        });
    });

    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

function createRippleEffect(event, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentNode.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                this.parentNode.classList.remove('focused');
                validateField(this);
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });

        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormError('Vui lòng kiểm tra lại thông tin nhập vào.');
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    field.classList.remove('is-valid', 'is-invalid');
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Trường này là bắt buộc.';
    }

    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Email không hợp lệ.';
        }
    }

    if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Mật khẩu phải có ít nhất 6 ký tự.';
        }
    }

    if (isValid) {
        field.classList.add('is-valid');
        removeFieldError(field);
    } else {
        field.classList.add('is-invalid');
        showFieldError(field, errorMessage);
    }

    return isValid;
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    return isValid;
}

function showFieldError(field, message) {
    removeFieldError(field);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        display: block;
        color: var(--danger-color);
        font-size: 0.875rem;
        margin-top: 0.25rem;
    `;

    field.parentNode.appendChild(errorDiv);
}

function removeFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function showFormError(message) {
    const existingError = document.querySelector('.form-error-alert');
    if (existingError) {
        existingError.remove();
    }

    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger form-error-alert animate-fade-in';
    errorAlert.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const form = document.querySelector('form');
    form.parentNode.insertBefore(errorAlert, form);

    setTimeout(() => {
        if (errorAlert.parentNode) {
            errorAlert.remove();
        }
    }, 5000);
}

function initThemeToggle() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);

    if (!document.querySelector('.theme-toggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'btn btn-outline-primary theme-toggle';
        themeToggle.innerHTML = `
            <i class="bi bi-${currentTheme === 'dark' ? 'sun' : 'moon'}"></i>
        `;
        themeToggle.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            border-radius: 50%;
            width: 3rem;
            height: 3rem;
            padding: 0;
            box-shadow: var(--shadow-lg);
        `;

        themeToggle.addEventListener('click', toggleTheme);
        document.body.appendChild(themeToggle);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = `<i class="bi bi-${newTheme === 'dark' ? 'sun' : 'moon'}"></i>`;
    }
}

function initScrollEffects() {
    let ticking = false;

    function updateScrollEffects() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero-section');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });

        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);
}

function showLoading(element, text = 'Đang tải...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `
        <span class="loading me-2"></span>
        ${text}
    `;
    element.disabled = true;

    return () => {
        element.innerHTML = originalContent;
    element.disabled = false;
    };
}

function showSuccess(message, duration = 3000) {
    const successAlert = document.createElement('div');
    successAlert.className = 'alert alert-success alert-dismissible fade show animate-fade-in';
    successAlert.innerHTML = `
        <i class="bi bi-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    successAlert.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 9999;
        min-width: 300px;
        box-shadow: var(--shadow-lg);
    `;

    document.body.appendChild(successAlert);

    setTimeout(() => {
        if (successAlert.parentNode) {
            successAlert.remove();
        }
    }, duration);
}

function showError(message, duration = 5000) {
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger alert-dismissible fade show animate-fade-in';
    errorAlert.innerHTML = `
        <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    errorAlert.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 9999;
        min-width: 300px;
        box-shadow: var(--shadow-lg);
    `;

    document.body.appendChild(errorAlert);

    setTimeout(() => {
        if (errorAlert.parentNode) {
            errorAlert.remove();
        }
    }, duration);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .focused {
        transform: scale(1.02);
        transition: transform 0.2s ease;
    }
    
    .search-suggestions {
        animation: slideDown 0.2s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .suggestion-item:hover {
        background-color: var(--gray-100);
    }
    
    [data-theme="dark"] {
        --gray-50: #0f172a;
        --gray-100: #1e293b;
        --gray-200: #334155;
        --gray-300: #475569;
        --gray-400: #64748b;
        --gray-500: #94a3b8;
        --gray-600: #cbd5e1;
        --gray-700: #e2e8f0;
        --gray-800: #f1f5f9;
        --gray-900: #f8fafc;
    }
`;

document.head.appendChild(style);

window.DigitalLibrary = {
    showLoading,
    showSuccess,
    showError,
    toggleTheme
}; 