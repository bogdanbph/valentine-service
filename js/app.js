document.addEventListener("DOMContentLoaded", function () {
    const noButton = document.getElementById("noButton");
    const yesButton = document.getElementById("yesButton");
    const valentineVideo = document.getElementById("valentineVideo");
    const textContainer = document.getElementById("textContainer");
    const textContainerFelcitari = document.getElementById("textContainerFelcitari");

    let currentScale = 1.0; // Track button scaling factor

    function getRandomPosition() {
        const maxTop = window.innerHeight - noButton.offsetHeight;
        const maxLeft = window.innerWidth - noButton.offsetWidth;

        return {
            top: Math.random() * maxTop,
            left: Math.random() * maxLeft
        };
    }

    function shrinkButton(button) {
        currentScale *= 0.85; // Reduce size by 15% each time
        button.style.transform = `scale(${currentScale})`;
    }

    yesButton.addEventListener("click", () => {
        valentineVideo.pause();
        valentineVideo.style.display = "none";
        yesButton.style.display = "none";
        noButton.style.display = "none";
        textContainer.style.display = "none";
        textContainerFelcitari.style.display = "flex";
    });

    noButton.addEventListener("click", function () {
        const newPos = getRandomPosition();
        this.style.top = `${newPos.top}px`;
        this.style.left = `${newPos.left}px`;
        shrinkButton(this);
    });

    // Mousemove event for desktop interactions
    if (!("ontouchstart" in document.documentElement)) {
        document.addEventListener("mousemove", function (event) {
            const buttonRect = noButton.getBoundingClientRect();
            const distance = Math.sqrt(
                Math.pow(event.clientX - (buttonRect.left + buttonRect.width / 2), 2) +
                Math.pow(event.clientY - (buttonRect.top + buttonRect.height / 2), 2)
            );

            if (distance < 50) {
                const newPos = getRandomPosition();
                noButton.style.top = `${newPos.top}px`;
                noButton.style.left = `${newPos.left}px`;
            }
        });
    }
});
