document.addEventListener("DOMContentLoaded", async function () {
    //  Verificar si hay una preferencia guardada en localStorage (Modo oscuro)
    const themeToggle = document.getElementById("theme-toggle");
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.checked = true;
    }

    // Evento para cambiar el tema
    themeToggle.addEventListener("change", function () {
        if (themeToggle.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
            document.getElementById("audio-oscuro").play();
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
            document.getElementById("audio-claro").play();
        }
    });

    //  Iniciar reconocimiento de voz automáticamente
    eel.start_listening();

    //  Inicializar síntesis de voz (Truco para evitar bloqueos)
    const synth = window.speechSynthesis;

    function inicializarVoz() {
        let utterance = new SpeechSynthesisUtterance(" ");
        synth.speak(utterance);
    }
    inicializarVoz(); // Llamada al inicio para desbloquear el sistema

    function hablarTexto(mensaje) {
        if (mensaje) {
            synth.cancel(); // Cancela cualquier mensaje en cola
            const utterance = new SpeechSynthesisUtterance(mensaje);
            utterance.lang = "es-ES";
            utterance.rate = 1;
            utterance.pitch = 1;
            synth.speak(utterance);
        }
    }

    async function esperarVocesYHablar() {
        await new Promise((resolve) => {
            let voces = synth.getVoices();
            if (voces.length > 0) {
                resolve();
            } else {
                synth.onvoiceschanged = () => resolve();
            }
        });

        setTimeout(() => hablarTexto("Hola, soy Ozuna Assistant, ¿en qué puedo ayudarte?"), 1500);
    }

    esperarVocesYHablar(); // ⬅ Ahora sí el saludo debería funcionar bien 🚀

    //  Animación visual del micrófono (Efecto círculo)
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 512;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        const circle = document.querySelector('.circle');

        function animate() {
            analyser.getByteFrequencyData(dataArray);
            let volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
            let scale = Math.max(1, Math.min((volume - 5) / 30, 2.5)); // Ajuste de sensibilidad
            circle.style.transform = `scale(${scale})`;
            let glowIntensity = Math.min(volume * 3, 150);
            circle.style.boxShadow = `0 0 ${40 + glowIntensity}px #1E90FF, 0 0 ${50 + glowIntensity}px rgba(30, 144, 255, 1), 0 0 ${120 + glowIntensity}px rgba(30, 144, 255, 0.8), 0 0 ${160 + glowIntensity}px rgba(30, 144, 255, 0.6)`;
            requestAnimationFrame(animate);
        }
        animate();
    } catch (err) {
        console.error('Error accediendo al micrófono:', err);
    }

    // Exponer funciones de actualización de texto y respuesta con Eel
    eel.expose(updateText);
    function updateText(text) {
        document.getElementById("texto").innerText = text;
    }

    eel.expose(updateResponse);
    function updateResponse(respuesta) {
        document.getElementById("respuesta").innerText = respuesta;
        hablarTexto(respuesta);
    }
});
