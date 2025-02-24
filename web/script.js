document.addEventListener("DOMContentLoaded", function () {
    // Verificar si hay una preferencia guardada en localStorage
    const themeToggle = document.getElementById("theme-toggle");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.checked = true;
    }

    // Cambiar el tema cuando se active el interruptor
    themeToggle.addEventListener("change", function () {
        if (themeToggle.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
        }
    });

    // Iniciar el reconocimiento de voz automáticamente
    eel.start_listening();
});

// Función para actualizar el texto reconocido en la interfaz
eel.expose(updateText);
function updateText(text) {
    document.getElementById("texto").innerText = text;
}
