
document.addEventListener("DOMContentLoaded", function () {
    const botaoContraste = document.getElementById("contraste");
    const botaoAumentar = document.getElementById("aumentar");
    const botaoDiminuir = document.getElementById("diminuir");

    let tamanhoFonte = Number(
        localStorage.getItem("tamanhoFonte") || 100
    );

    if (!Number.isFinite(tamanhoFonte)) {
        tamanhoFonte = 100;
    }

    tamanhoFonte = Math.max(80, Math.min(tamanhoFonte, 150));

    let contrasteAtivo =
        localStorage.getItem("altoContraste") === "true";

    function aplicarPreferencias() {
        document.body.classList.toggle(
            "alto-contraste",
            contrasteAtivo
        );

        document.documentElement.style.fontSize =
            tamanhoFonte + "%";

        if (botaoContraste) {
            botaoContraste.setAttribute(
                "aria-pressed",
                String(contrasteAtivo)
            );

            botaoContraste.textContent = contrasteAtivo
                ? "Contraste normal"
                : "Alto contraste";
        }
    }

    aplicarPreferencias();

    if (botaoContraste) {
        botaoContraste.addEventListener("click", function () {
            contrasteAtivo = !contrasteAtivo;

            localStorage.setItem(
                "altoContraste",
                String(contrasteAtivo)
            );

            aplicarPreferencias();
        });
    }

    if (botaoAumentar) {
        botaoAumentar.addEventListener("click", function () {
            tamanhoFonte = Math.min(tamanhoFonte + 10, 150);
            localStorage.setItem("tamanhoFonte", String(tamanhoFonte));
            aplicarPreferencias();
        });
    }

    if (botaoDiminuir) {
        botaoDiminuir.addEventListener("click", function () {
            tamanhoFonte = Math.max(tamanhoFonte - 10, 80);
            localStorage.setItem("tamanhoFonte", String(tamanhoFonte));
            aplicarPreferencias();
        });
    }
});