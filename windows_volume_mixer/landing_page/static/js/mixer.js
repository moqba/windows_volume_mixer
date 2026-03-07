document.addEventListener('DOMContentLoaded', () => {
    const { sliders, port } = window.MQ_CONFIG;
    const host = window.location.hostname;

    if (!sliders || sliders.length === 0) return;

    const BASE_URL = `http://${host}:${port}`;
    const ICON_CACHE_PREFIX = 'icon-cache-';
    const MAX_ICON_RETRIES = 5;
    const ICON_RETRY_MS = 2000;
    const VOLUME_DEBOUNCE_MS = 80;
    const GAME_POLL_MS = 2000;
    const SSE_RECONNECT_MS = 2000;

    const dynamicSliderName = sliders.find(name => name === 'game') ?? null;
    const staticApps = sliders.filter(name => name !== 'game');

    // --- Utilities ---

    function debounce(fn, delay) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    }

    function createFallbackIcon(app) {
        const div = document.createElement('div');
        div.className = 'icon-fallback';
        div.textContent = app[0].toUpperCase();
        return div;
    }

    function blobToBase64(blob) {
        return new Promise(resolve => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    }

    // --- Icon loading ---

    async function tryLoadIcon(app, container) {
        const cacheKey = `${ICON_CACHE_PREFIX}${app}`;
        const cached = localStorage.getItem(cacheKey);

        container.innerHTML = '';

        if (cached) {
            const img = document.createElement('img');
            img.src = cached;
            img.className = 'icon-img';
            container.appendChild(img);
            return;
        }

        container.appendChild(createFallbackIcon(app));

        let attempts = 0;

        async function attempt() {
            if (attempts >= MAX_ICON_RETRIES) return;
            attempts++;
            try {
                const res = await fetch(`${BASE_URL}/icon/${app}`);
                if (!res.ok) throw new Error();
                const blob = await res.blob();
                const base64 = await blobToBase64(blob);
                try {
                    localStorage.setItem(cacheKey, base64);
                } catch {
                    // localStorage full — skip caching
                }
                const img = document.createElement('img');
                img.src = base64;
                img.className = 'icon-img';
                container.innerHTML = '';
                container.appendChild(img);
            } catch {
                if (attempts < MAX_ICON_RETRIES) {
                    setTimeout(attempt, ICON_RETRY_MS);
                }
            }
        }

        attempt(); // try immediately, retry on failure
    }

    // --- SSE helper ---

    function openVolumeSSE(app, { onValue, onDisconnect }) {
        const es = new EventSource(`${BASE_URL}/volume/${app}`);
        es.onmessage = event => {
            const value = parseFloat(event.data);
            if (!isNaN(value)) onValue(value);
        };
        es.onerror = () => {
            es.close();
            onDisconnect();
        };
        return es;
    }

    // --- Volume update ---

    async function updateVolume(app, value) {
        try {
            await fetch(`${BASE_URL}/set-volume`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ app, value })
            });
        } catch (err) {
            console.error('Failed to update volume:', err);
        }
    }

    // --- Static channels ---

    staticApps.forEach(app => {
        const slider = document.getElementById(`${app}-slider`);
        const display = document.getElementById(`${app}-val`);
        const channel = document.getElementById(`${app}-container`);
        const iconContainer = document.getElementById(`${app}-icon`);

        const debouncedUpdate = debounce(updateVolume, VOLUME_DEBOUNCE_MS);

        function setInactive() {
            channel.classList.add('inactive');
            slider.disabled = true;
            display.textContent = '--';
        }

        function setActive() {
            channel.classList.remove('inactive');
            slider.disabled = false;
        }

        function connect() {
            openVolumeSSE(app, {
                onValue(value) {
                    setActive();
                    if (document.activeElement !== slider) {
                        slider.value = value;
                        display.textContent = value.toFixed(2);
                    }
                },
                onDisconnect() {
                    setInactive();
                    setTimeout(connect, SSE_RECONNECT_MS);
                }
            });
        }

        setInactive();
        connect();
        tryLoadIcon(app, iconContainer);

        slider.addEventListener('input', () => {
            const value = parseFloat(slider.value);
            display.textContent = value.toFixed(2);
            debouncedUpdate(app, value);
        });
    });

    // --- Dynamic game channel ---

    if (!dynamicSliderName) return;

    const gameChannel = document.getElementById('game-container');
    const gameSlider = document.getElementById('game-slider');
    const gameDisplay = document.getElementById('game-val');
    const gameIcon = document.getElementById('game-icon');
    const gameLabel = gameChannel.querySelector('.label');

    let currentGame = null;
    let gameEventSource = null;
    let gameSliderAbort = null;

    const debouncedGameUpdate = debounce(updateVolume, VOLUME_DEBOUNCE_MS);

    function resetGameChannel() {
        gameChannel.classList.add('inactive');
        gameSlider.disabled = true;
        gameDisplay.textContent = '--';
        gameLabel.textContent = 'Game';
        gameIcon.innerHTML = '';
        gameIcon.appendChild(createFallbackIcon('game'));

        if (gameEventSource) {
            gameEventSource.close();
            gameEventSource = null;
        }

        currentGame = null;
    }

    async function pollGame() {
        try {
            const res = await fetch(`${BASE_URL}/game`);
            if (!res.ok) { resetGameChannel(); return; }

            const data = await res.json();
            if (!data.value) { resetGameChannel(); return; }

            const gameName = data.value;
            if (currentGame === gameName) return;

            currentGame = gameName;
            gameChannel.classList.remove('inactive');
            gameSlider.disabled = false;
            gameLabel.textContent = gameName;

            tryLoadIcon(gameName, gameIcon);

            if (gameEventSource) gameEventSource.close();
            gameEventSource = openVolumeSSE(gameName, {
                onValue(value) {
                    if (document.activeElement !== gameSlider) {
                        gameSlider.value = value;
                        gameDisplay.textContent = value.toFixed(2);
                    }
                },
                onDisconnect() {} // pollGame drives reconnect logic
            });

            // Replace previous input listener cleanly
            if (gameSliderAbort) gameSliderAbort.abort();
            gameSliderAbort = new AbortController();
            gameSlider.addEventListener('input', () => {
                const value = parseFloat(gameSlider.value);
                gameDisplay.textContent = value.toFixed(2);
                debouncedGameUpdate(gameName, value);
            }, { signal: gameSliderAbort.signal });

        } catch (err) {
            console.error('Poll game failed:', err);
        }
    }

    resetGameChannel();
    setInterval(pollGame, GAME_POLL_MS);
});
