// Simple mobile nav toggle placeholder (sidebar is hidden on mobile in favor of bottom nav).
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('mobileNavToggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      alert('Use the bottom navigation bar to move between sections on mobile.');
    });
  }
});
