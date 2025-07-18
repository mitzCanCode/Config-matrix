// Global Alert System
/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of alert ('success', 'error', 'warning', 'info')
 * @param {number} duration - How long to show the toast (in milliseconds)
 */
function showToast(message, type = 'success', duration = 10000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed top-0 end-0 p-3 toast-container';
        toastContainer.style.zIndex = '9999';
        toastContainer.style.pointerEvents = 'none';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const alertClass = type === 'error' ? 'danger' : type === 'warning' ? 'warning' : type === 'info' ? 'info' : 'success';
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `alert alert-${alertClass} alert-dismissible fade show toast-enhanced`;
    toast.setAttribute('role', 'alert');
    toast.style.pointerEvents = 'auto';
    toast.style.maxWidth = '400px';
    toast.style.position = 'relative';
    toast.style.overflow = 'hidden';
    toast.style.backdropFilter = 'blur(10px)';
    toast.style.background = `rgba(var(--toast-bg-${alertClass}), 0.9)`;
    toast.style.border = `1px solid rgba(var(--toast-border-${alertClass}), 0.3)`;
    toast.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.3)';
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'toast-progress-bar';
    progressBar.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        width: 100%;
        background: rgba(var(--toast-progress-${alertClass}), 0.8);
        transform-origin: left;
        transition: transform linear;
        z-index: 10;
    `;
    
    toast.innerHTML = `
        <div style="position: relative; z-index: 5;">
            ${message}
        </div>
    `;
    
    // Add progress bar to toast
    toast.appendChild(progressBar);
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Animate progress bar
    setTimeout(() => {
        progressBar.style.transitionDuration = `${duration}ms`;
        progressBar.style.transform = 'scaleX(0)';
    }, 100);
    
    // Auto-remove after specified duration
    const removeTimeout = setTimeout(() => {
        if (document.getElementById(toastId)) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 150);
        }
    }, duration);
    
    // Handle manual dismiss by clicking anywhere on the toast
    toast.addEventListener('click', () => {
        clearTimeout(removeTimeout);
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 150);
    });
    
    // Add cursor pointer to indicate it's clickable
    toast.style.cursor = 'pointer';
}

// Convert Flask flash messages to toast notifications
document.addEventListener('DOMContentLoaded', function() {
    // Find and convert only flash messages (those in the flash message container)
    // Use the specific flash-messages-container class to avoid picking up other elements
    const flashContainer = document.querySelector('.flash-messages-container');
    if (flashContainer) {
        const flashMessages = flashContainer.querySelectorAll('.alert');
        flashMessages.forEach(alert => {
            // Skip if it's already a toast (has toast-container parent)
            if (alert.closest('.toast-container')) {
                return;
            }
            
            // Extract message and type - get text content but exclude button text
            const alertText = alert.cloneNode(true);
            const button = alertText.querySelector('.btn-close');
            if (button) {
                button.remove();
            }
            const message = alertText.textContent.trim();
            
            const type = alert.classList.contains('alert-danger') ? 'error' : 
                        alert.classList.contains('alert-warning') ? 'warning' : 
                        alert.classList.contains('alert-info') ? 'info' : 'success';
            
            // Remove the original alert
            alert.remove();
            
            // Show as toast
            showToast(message, type);
        });
        
        // Remove the flash container if it's empty
        if (flashContainer.children.length === 0) {
            flashContainer.remove();
        }
    }
});

// Make showToast available globally
window.showToast = showToast;
