/**
 * Password Visibility Toggle Module
 * Handles password field visibility toggle functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('togglePassword');
    const passwordField = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (toggleButton && passwordField && toggleIcon) {
        toggleButton.addEventListener('click', function() {
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                toggleIcon.className = 'bi bi-eye-slash';
            } else {
                passwordField.type = 'password';
                toggleIcon.className = 'bi bi-eye';
            }
        });
    }
});
