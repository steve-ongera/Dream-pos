document.addEventListener('DOMContentLoaded', function() {
    // Initialize login functionality
    initializeLoginForm();
    initializePasswordToggle();
    initializeFormValidation();
    initializeAnimations();
});

/**
 * Initialize login form functionality
 */
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const loadingSpinner = loginBtn.querySelector('.loading-spinner');
    
    loginForm.addEventListener('submit', function(e) {
        // Show loading state
        showLoadingState(loginBtn, btnText, loadingSpinner);
        
        // Basic validation before submission
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        if (!username || !password) {
            e.preventDefault();
            hideLoadingState(loginBtn, btnText, loadingSpinner);
            showError('Please fill in all required fields.');
            return;
        }
        
        // Form will submit normally if validation passes
    });
    
    // Reset loading state if there are server-side errors
    const messages = document.querySelector('.messages');
    if (messages && messages.querySelector('.alert-error')) {
        hideLoadingState(loginBtn, btnText, loadingSpinner);
    }
}

/**
 * Initialize password visibility toggle
 */
function initializePasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (!togglePassword || !passwordInput || !toggleIcon) return;
    
    togglePassword.addEventListener('click', function() {
        const isPassword = passwordInput.type === 'password';
        
        // Toggle password visibility
        passwordInput.type = isPassword ? 'text' : 'password';
        
        // Update icon with smooth transition
        toggleIcon.style.opacity = '0.5';
        setTimeout(() => {
            toggleIcon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
            toggleIcon.style.opacity = '1';
        }, 100);
        
        // Update button accessibility
        togglePassword.setAttribute('aria-label', 
            isPassword ? 'Hide password' : 'Show password'
        );
        
        // Keep focus on password input
        passwordInput.focus();
    });
    
    // Set initial accessibility attribute
    togglePassword.setAttribute('aria-label', 'Show password');
    togglePassword.setAttribute('title', 'Show password');
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Real-time validation feedback
    [usernameInput, passwordInput].forEach(input => {
        if (!input) return;
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
        
        // Handle Enter key navigation
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                if (this === usernameInput) {
                    passwordInput.focus();
                    e.preventDefault();
                } else if (this === passwordInput) {
                    document.getElementById('loginForm').requestSubmit();
                }
            }
        });
    });
}

/**
 * Initialize animations and interactions
 */
function initializeAnimations() {
    // Add focus animations to input groups
    const inputGroups = document.querySelectorAll('.input-group');
    
    inputGroups.forEach(group => {
        const input = group.querySelector('input');
        const icon = group.querySelector('.input-icon');
        
        if (!input || !icon) return;
        
        input.addEventListener('focus', function() {
            group.classList.add('focused');
            icon.style.color = 'var(--primary-color)';
            icon.style.transform = 'scale(1.1)';
        });
        
        input.addEventListener('blur', function() {
            group.classList.remove('focused');
            icon.style.color = 'var(--text-light)';
            icon.style.transform = 'scale(1)';
        });
    });
    
    // Add hover effects to form elements
    const interactiveElements = document.querySelectorAll('input, button, a, .checkbox-container');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Auto-hide messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            hideMessage(alert);
        }, 5000);
    });
}

/**
 * Validate individual form fields
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    
    clearFieldError(field);
    
    if (!value) {
        showFieldError(field, 'This field is required.');
        return false;
    }
    
    if (field.name === 'username') {
        if (value.length < 3) {
            showFieldError(field, 'Username must be at least 3 characters long.');
            return false;
        }
        
        // Check if it's an email format
        if (value.includes('@') && !isValidEmail(value)) {
            showFieldError(field, 'Please enter a valid email address.');
            return false;
        }
    }
    
    if (field.name === 'password') {
        if (value.length < 6) {
            showFieldError(field, 'Password must be at least 6 characters long.');
            return false;
        }
    }
    
    return true;
}

/**
 * Show field-specific error
 */
function showFieldError(field, message) {
    const inputGroup = field.closest('.input-group');
    const formGroup = field.closest('.form-group');
    
    // Add error styling
    field.style.borderColor = 'var(--error-color)';
    inputGroup.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    
    // Create or update error message
    let errorElement = formGroup.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('span');
        errorElement.className = 'field-error';
        errorElement.style.cssText = `
            color: var(--error-color);
            font-size: 0.8rem;
            display: block;
            margin-top: 4px;
            animation: slideDown 0.3s ease-out;
        `;
        formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    const inputGroup = field.closest('.input-group');
    const formGroup = field.closest('.form-group');
    const errorElement = formGroup.querySelector('.field-error');
    
    // Reset styling
    field.style.borderColor = '';
    inputGroup.style.boxShadow = '';
    
    // Remove error message
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Show loading state on login button
 */
function showLoadingState(button, textElement, spinner) {
    button.disabled = true;
    textElement.style.opacity = '0';
    spinner.style.display = 'inline-block';
    button.style.cursor = 'not-allowed';
}

/**
 * Hide loading state on login button
 */
function hideLoadingState(button, textElement, spinner) {
    button.disabled = false;
    textElement.style.opacity = '1';
    spinner.style.display = 'none';
    button.style.cursor = 'pointer';
}

/**
 * Show error message
 */
function showError(message) {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-error';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
    `;
    
    messagesContainer.appendChild(alertDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideMessage(alertDiv);
    }, 5000);
}

/**
 * Create messages container if it doesn't exist
 */
function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    
    const form = document.getElementById('loginForm');
    form.parentNode.insertBefore(container, form);
    
    return container;
}

/**
 * Hide message with animation
 */
function hideMessage(messageElement) {
    messageElement.style.animation = 'slideUp 0.3s ease-out forwards';
    messageElement.addEventListener('animationend', function() {
        if (this.parentNode) {
            this.parentNode.removeChild(this);
        }
    });
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Focus username field with Ctrl/Cmd + L
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        document.getElementById('username').focus();
    }
    
    // Toggle password visibility with Ctrl/Cmd + Shift + P
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        document.getElementById('togglePassword').click();
    }
});

/**
 * Handle form auto-fill detection
 */
function detectAutoFill() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    inputs.forEach(input => {
        // Check for auto-filled values
        setInterval(() => {
            if (input.value && !input.dataset.filled) {
                input.dataset.filled = 'true';
                input.dispatchEvent(new Event('input'));
            }
        }, 500);
    });
}

// Initialize auto-fill detection
detectAutoFill();

// Add slideUp animation for hiding messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
            max-height: 100px;
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
            max-height: 0;
            margin: 0;
            padding: 0;
        }
    }
    
    .input-group.focused input {
        transform: translateY(-1px);
    }
    
    .field-error {
        animation: slideDown 0.3s ease-out;
    }
`;
document.head.appendChild(style);

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Add ARIA labels and descriptions
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    const loginForm = document.getElementById('loginForm');
    
    if (usernameInput) {
        usernameInput.setAttribute('aria-describedby', 'username-help');
        usernameInput.setAttribute('aria-required', 'true');
    }
    
    if (passwordInput) {
        passwordInput.setAttribute('aria-describedby', 'password-help');
        passwordInput.setAttribute('aria-required', 'true');
    }
    
    if (togglePassword) {
        togglePassword.setAttribute('type', 'button');
        togglePassword.setAttribute('tabindex', '0');
    }
    
    if (loginForm) {
        loginForm.setAttribute('novalidate', 'true'); // Use custom validation
    }
    
    // Announce form errors to screen readers
    const announceError = (message) => {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    };
    
    // Monitor for error messages and announce them
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains('alert-error')) {
                        announceError(node.textContent);
                    }
                });
            }
        });
    });
    
    const messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        observer.observe(messagesContainer, { childList: true });
    }
}

// Initialize accessibility features
initializeAccessibility();

/**
 * Handle network connectivity
 */
function handleNetworkStatus() {
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    
    window.addEventListener('online', () => {
        if (loginBtn.disabled) {
            loginBtn.disabled = false;
            btnText.textContent = 'Sign In';
            loginBtn.style.background = 'linear-gradient(135deg, var(--primary-color) 0%, #0891b2 100%)';
        }
    });
    
    window.addEventListener('offline', () => {
        loginBtn.disabled = true;
        btnText.textContent = 'No Internet Connection';
        loginBtn.style.background = '#6b7280';
        
        showError('Please check your internet connection and try again.');
    });
}

// Initialize network status handling
handleNetworkStatus();

/**
 * Enhanced security features
 */
function initializeSecurityFeatures() {
    const passwordInput = document.getElementById('password');
    const usernameInput = document.getElementById('username');
    
    // Prevent password auto-complete in development (optional)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        passwordInput.setAttribute('autocomplete', 'new-password');
    }
    
    // Clear sensitive data on page unload
    window.addEventListener('beforeunload', () => {
        if (passwordInput) {
            passwordInput.value = '';
        }
    });
    
    // Detect and handle potential security issues
    let failedAttempts = 0;
    const maxFailedAttempts = 3;
    
    document.addEventListener('submit', (e) => {
        if (e.target.id === 'loginForm') {
            // This will be handled by Django on the backend
            // but we can track client-side attempts for UX
            const messages = document.querySelector('.messages');
            if (messages && messages.querySelector('.alert-error')) {
                failedAttempts++;
                
                if (failedAttempts >= maxFailedAttempts) {
                    showError('Multiple failed login attempts detected. Please wait a moment before trying again.');
                    
                    // Disable form for 30 seconds
                    const loginBtn = document.getElementById('loginBtn');
                    const btnText = loginBtn.querySelector('.btn-text');
                    
                    loginBtn.disabled = true;
                    btnText.textContent = 'Please wait...';
                    
                    setTimeout(() => {
                        loginBtn.disabled = false;
                        btnText.textContent = 'Sign In';
                        failedAttempts = 0;
                    }, 30000);
                }
            }
        }
    });
}

// Initialize security features
initializeSecurityFeatures();

/**
 * Performance optimizations
 */
function optimizePerformance() {
    // Debounce validation to avoid excessive calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Apply debounced validation to inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        const debouncedValidation = debounce(() => validateField(input), 300);
        input.addEventListener('input', debouncedValidation);
    });
    
    // Lazy load animations for better performance
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    });
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.login-card, .circle');
    animatedElements.forEach(el => observer.observe(el));
}

// Initialize performance optimizations
optimizePerformance();

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateField,
        isValidEmail,
        showError,
        hideMessage
    };
}