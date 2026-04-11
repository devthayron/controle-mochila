/* ─────────────────────────────────────────────────────────
   base.js — Controle de Mochila · TI Armazém Paraíba
   ───────────────────────────────────────────────────────── */

/**
 * Toggle da sidebar (mobile)
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

/**
 * Inicialização geral da aplicação
 */
document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById('sidebar');

    /* ─── FECHAR SIDEBAR AO CLICAR FORA ─── */
    document.addEventListener('click', function (e) {
        if (!sidebar) return;

        const isOpen = sidebar.classList.contains('open');
        const clickedOutside = !sidebar.contains(e.target);
        const clickedHamburger = e.target.closest('.hamburger');

        if (isOpen && clickedOutside && !clickedHamburger) {
            sidebar.classList.remove('open');
        }
    });

    /* ─── LOGOUT ─── */
    const logoutBtn = document.querySelector(".js-logout");
    const logoutForm = document.getElementById("logout-form");

    if (logoutBtn && logoutForm) {
        logoutBtn.addEventListener("click", function (e) {
            e.preventDefault();
            logoutForm.submit();
        });
    }

});