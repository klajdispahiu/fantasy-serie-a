// Global utility — CSRF helper for all fetch requests
function getCsrf() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// Auto-dismiss messages after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transition = 'opacity 0.5s';
      setTimeout(() => msg.remove(), 500);
    }, 4000);
  });
});