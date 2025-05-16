document.addEventListener("DOMContentLoaded", async function () {
    const themeToggle = document.getElementById("theme-toggle");

    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.checked = true;
    }

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

    // Inicializar síntesis de voz
    const synth = window.speechSynthesis;
    function inicializarVoz() {
        let utterance = new SpeechSynthesisUtterance(" ");
        synth.speak(utterance);
    }
    inicializarVoz();

    function hablarTexto(mensaje) {
        if (mensaje) {
            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(mensaje);
            utterance.lang = "es-ES";
            utterance.rate = 1;
            utterance.pitch = 1;

            eel.pausar_escucha(); // Pausar escucha antes de hablar

            // Reanudar escucha después de hablar
            utterance.onend = () => {
                console.log("✅ Texto hablado, reanudando escucha...");
                eel.reanudar_escucha();
            };

            synth.speak(utterance);
        }
    }

    async function esperarVocesYHablar() {
        await new Promise((resolve) => {
            let voces = synth.getVoices();
            if (voces.length > 0) resolve();
            else synth.onvoiceschanged = () => resolve();
        });

        const mensaje = "Hola, soy Ozuna Assistant, ¿en qué puedo ayudarte?";
        const utterance = new SpeechSynthesisUtterance(mensaje);
        utterance.lang = "es-ES";
        utterance.rate = 1;
        utterance.pitch = 1;

        eel.pausar_escucha(); // Pausar escucha durante el saludo

        // ⏱️ Plan B: Iniciar escucha manualmente si onend no se dispara
        let inicioForzado = setTimeout(() => {
            console.warn("⚠️ No se detectó onend. Iniciando escucha forzada...");
            eel.reanudar_escucha();
            eel.start_listening();
        }, 5000); // 5 segundos como margen seguro

        utterance.onend = () => {
            clearTimeout(inicioForzado);
            console.log("✅ Saludo finalizado, iniciando escucha");
            eel.reanudar_escucha();
            eel.start_listening();
        };

        synth.speak(utterance);
    }

    esperarVocesYHablar();

    // Variable global que ya deberías tener

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

        if (micMuted) {
            // Visual de micrófono apagado
            circle.style.transform = `scale(1)`;
            circle.style.boxShadow = `0 0 20px gray`;
        } else {
            // Visual de micrófono activo
            let volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
            let scale = Math.max(1, Math.min((volume - 35) / 30, 2.5));
            let glow = Math.min(volume * 3, 150);

            circle.style.transform = `scale(${scale})`;
            circle.style.boxShadow = `
                0 0 ${40 + glow}px #1E90FF,
                0 0 ${50 + glow}px rgba(30, 144, 255, 1),
                0 0 ${120 + glow}px rgba(30, 144, 255, 0.8)
            `;
        }

        requestAnimationFrame(animate);
    }

    animate();
} catch (err) {
    console.error('❌ Error accediendo al micrófono para animación:', err);
}


    // Exposición para Eel: Texto transcrito
    eel.expose(updateText);
    function updateText(text) {
        document.getElementById("texto").innerText = text;
    }

    // Exposición para Eel: Respuesta del asistente
    eel.expose(updateResponse);
    function updateResponse(respuesta) {
        const respuestaEl = document.getElementById("respuesta");
        respuestaEl.classList.remove("visible");
        respuestaEl.textContent = respuesta;
        void respuestaEl.offsetWidth;
        respuestaEl.classList.add("visible");
        hablarTexto(respuesta);
    }

// Preguntas frecuentes
async function cargarTopPreguntas() {
    const top = await eel.get_top_questions()();
    const lista = document.getElementById("question-list");
    lista.innerHTML = "";

    if (top.length === 0) {
        lista.innerHTML = "<li>No hay preguntas registradas aún.</li>";
    } else {
        top.forEach(q => {
            const li = document.createElement("li");
            li.textContent = q.question;

            // Añadir evento para ejecutar la pregunta al hacer clic
            li.addEventListener("click", async () => {
                document.getElementById("texto").innerText = q.question;

                // Llamamos al backend como si fuera voz reconocida
                const respuesta = await eel.simular_comando(q.question)(); // <-- función que debes exponer
                updateResponse(respuesta);
            });

            lista.appendChild(li);
        });
    }
}


    cargarTopPreguntas();

    // Botón de limpieza
    const clearBtn = document.getElementById("clear");
    clearBtn.addEventListener("click", () => {
        document.getElementById("texto").innerText = "";
        document.getElementById("respuesta").innerText = "";
    });


    //boton de micrófono y estado
    const micBtn = document.getElementById("microfono");
    let micMuted = false;

    micBtn.addEventListener("click", () => {
    micMuted = !micMuted;

    if (micMuted) {
        console.log("🔇 Micrófono silenciado");
        eel.pausar_escucha();  // Llama a Python
        micBtn.textContent = "🔇";
        micBtn.title = "Activar micrófono";
    } else {
        console.log("🎙️ Micrófono activado");
        eel.reanudar_escucha();  // Llama a Python
        micBtn.textContent = "🎙️";
        micBtn.title = "Silenciar micrófono";
    }
});





});
