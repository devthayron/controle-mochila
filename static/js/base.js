/* ─────────────────────────────────────────────────────────
   base.js — Controle de Mochila · TI Armazém Paraíba
   ───────────────────────────────────────────────────────── */

/**
 * Abre/fecha a sidebar em telas pequenas (mobile).
 */
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

/**
 * Fecha a sidebar ao clicar fora dela.
 */
document.addEventListener('click', function (e) {
    const sidebar = document.getElementById('sidebar');
    const isOpen  = sidebar.classList.contains('open');
    const clickedOutside = !sidebar.contains(e.target);
    const clickedHamburger = e.target.closest('.hamburger');

    if (isOpen && clickedOutside && !clickedHamburger) {
        sidebar.classList.remove('open');
    }
});
