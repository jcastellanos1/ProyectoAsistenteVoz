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
            // Reproducir audio para modo oscuro
            const audioOscuro = document.getElementById("audio-oscuro");
            audioOscuro.play();
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
            // Reproducir audio para modo claro
            const audioClaro = document.getElementById("audio-claro");
            audioClaro.play();
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

async function startVisualizer() {
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
            let scale = Math.max(1, Math.min((volume - 5) / 7, 2.5)); // Ajuste de sensibilidad y máximo tamaño
            circle.style.transform = `scale(${scale})`;
            let glowIntensity = Math.min(volume * 3, 150);
            circle.style.boxShadow = `0 0 ${40 + glowIntensity}px #1E90FF, 0 0 ${50 + glowIntensity}px rgba(30, 144, 255, 1), 0 0 ${120 + glowIntensity}px rgba(30, 144, 255, 0.8), 0 0 ${160 + glowIntensity}px rgba(30, 144, 255, 0.6)`;
            requestAnimationFrame(animate);
        }
        animate();
    } catch (err) {
        console.error('Error accessing microphone:', err);
    }
}
startVisualizer();
