// navigation.js - versión robusta
document.addEventListener('DOMContentLoaded', function () {
  function toggleLogo() {
    try {
      const logoLight = document.getElementById('logo-light');
      const logoDark = document.getElementById('logo-dark');

      if (!logoLight || !logoDark) {
        console.warn("navigation.js: no se encontraron #logo-light o #logo-dark en el DOM");
        return;
      }

      const isDark = document.documentElement.classList.contains('dark');

      // usar style.display directamente; también mantenemos clases tailwind si quieres
      logoLight.style.display = isDark ? 'none' : 'block';
      logoDark.style.display = isDark ? 'block' : 'none';
    } catch (err) {
      console.error("navigation.js error:", err);
    }
  }

  // Ejecutar al cargar
  toggleLogo();

  // Observar clase 'dark' en <html>
  const observer = new MutationObserver(toggleLogo);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
});
