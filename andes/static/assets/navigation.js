document.addEventListener('DOMContentLoaded', function () {
  function toggleLogo() {
    const logoLight = document.getElementById('logo-light');
    const logoDark = document.getElementById('logo-dark');

    // Verifica si el modo oscuro está activo
    if (document.documentElement.classList.contains('dark')) {
      logoDark.style.display = 'block';  // Muestra el logo oscuro
      logoLight.style.display = 'none';  // Oculta el logo claro
    } else {
      logoLight.style.display = 'block'; // Muestra el logo claro
      logoDark.style.display = 'none';   // Oculta el logo oscuro
    }
  }

  // Llama a la función al cargar la página
  toggleLogo();

  // Observa cambios en el modo claro/oscuro
  const observer = new MutationObserver(toggleLogo);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  });
});