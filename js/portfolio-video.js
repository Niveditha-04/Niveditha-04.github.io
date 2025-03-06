document.addEventListener("DOMContentLoaded", function () {
    var video = document.getElementById("portfolio-video");
    var playButton = document.getElementById("playButton");

    if (video && playButton) {
        playButton.addEventListener("click", function () {
            if (video.paused) {
                video.play();
                playButton.style.display = "none"; // Hide play button after clicking
            } else {
                video.pause();
                playButton.style.display = "block"; // Show button again when paused
            }
        });
    }
});
