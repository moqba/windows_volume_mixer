document.addEventListener('DOMContentLoaded', () => {
    const { sliders, port } = window.MQ_CONFIG;
    const host = window.location.hostname;

    if (!sliders || sliders.length === 0) return;

    const dynamicSliderName = sliders[0] === "game" ? "game" : null;
    const staticApps = sliders.filter(name => name !== dynamicSliderName);

    let dynamicGame = null;
    let dynamicEventSource = null;

    let dynamicGameChannel = dynamicSliderName
        ? document.getElementById(`${dynamicSliderName}-container`)
        : null;
    let dynamicGameSlider = dynamicSliderName
        ? document.getElementById(`${dynamicSliderName}-slider`)
        : null;
    let dynamicGameDisplay = dynamicSliderName
        ? document.getElementById(`${dynamicSliderName}-val`)
        : null;

    function createFallbackIcon(app) {
        const div = document.createElement('div');
        div.className = 'icon-fallback';
        div.innerText = app[0].toUpperCase();
        return div;
    }

    function blobToBase64(blob) {
        return new Promise(resolve => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        });
    }

    async function tryLoadIcon(app, container) {
        const cacheKey = `icon-cache-${app}`;
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

        async function fetchIcon() {
            try {
                const res = await fetch(`http://${host}:${port}/icon/${app}`);
                if (!res.ok) throw new Error();

                const blob = await res.blob();
                const base64 = await blobToBase64(blob);
                localStorage.setItem(cacheKey, base64);

                const img = document.createElement('img');
                img.src = base64;
                img.className = 'icon-img';

                container.innerHTML = '';
                container.appendChild(img);
                return true;
            } catch {
                return false;
            }
        }

        const interval = setInterval(async () => {
            const success = await fetchIcon();
            if (success) clearInterval(interval);
        }, 2000);
    }

    staticApps.forEach(app => {
        const slider = document.getElementById(`${app}-slider`);
        const display = document.getElementById(`${app}-val`);
        const channel = document.getElementById(`${app}-container`);

        function setInactive() {
            channel.classList.add('inactive');
            slider.disabled = true;
            display.innerText = '--';
        }

        function setActive() {
            channel.classList.remove('inactive');
            slider.disabled = false;
        }

        let eventSource = null;

        function connectSSE() {
            if (eventSource) eventSource.close();

            eventSource = new EventSource(`http://${host}:${port}/volume/${app}`);
            eventSource.onmessage = event => {
                const value = parseFloat(event.data);
                if (isNaN(value)) return;

                setActive();
                if (document.activeElement !== slider) {
                    slider.value = value;
                    display.innerText = value.toFixed(2);
                }
            };

            eventSource.onerror = () => {
                eventSource.close();
                setInactive();
                setTimeout(connectSSE, 2000);
            };
        }

        setInactive();
        connectSSE();
        tryLoadIcon(app, document.getElementById(`${app}-icon`));

        slider.addEventListener('input', () => {
            const value = parseFloat(slider.value);
            display.innerText = value.toFixed(2);
            updateVolume(app, value);
        });
    });

    async function pollGame() {
        if (!dynamicSliderName) return;

        try {
            const res = await fetch(`http://${host}:${port}/game`);
            const data = await res.json();

            if (!data.value) {
                dynamicGameChannel.classList.add('inactive');
                dynamicGameSlider.disabled = true;
                dynamicGameDisplay.innerText = '--';

                if (dynamicEventSource) {
                    dynamicEventSource.close();
                    dynamicEventSource = null;
                }

                dynamicGame = null;
                dynamicGameChannel.querySelector('.label').innerText = 'Game';
                dynamicGameChannel.querySelector('#game-icon').innerHTML =
                    '<div class="icon-fallback">G</div>';
                return;
            }

            const gameName = data.value;

            if (dynamicGame !== gameName) {
                dynamicGame = gameName;

                dynamicGameChannel.classList.remove('inactive');
                dynamicGameSlider.disabled = false;
                dynamicGameChannel.querySelector('.label').innerText = gameName;

                tryLoadIcon(gameName, document.getElementById('game-icon'));

                if (dynamicEventSource) dynamicEventSource.close();

                dynamicEventSource = new EventSource(
                    `http://${host}:${port}/volume/${gameName}`
                );

                dynamicEventSource.onmessage = event => {
                    const value = parseFloat(event.data);
                    if (isNaN(value)) return;

                    if (document.activeElement !== dynamicGameSlider) {
                        dynamicGameSlider.value = value;
                        dynamicGameDisplay.innerText = value.toFixed(2);
                    }
                };

                dynamicGameSlider.addEventListener('input', () => {
                    const value = parseFloat(dynamicGameSlider.value);
                    dynamicGameDisplay.innerText = value.toFixed(2);
                    updateVolume(gameName, value);
                });
            }

        } catch (err) {
            console.error('Poll game failed:', err);
        }
    }

    setInterval(pollGame, 2000);

    async function updateVolume(app, value) {
        try {
            await fetch(`http://${host}:${port}/set-volume`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ app, value })
            });
        } catch (err) {
            console.error('Failed to update volume:', err);
        }
    }

});
