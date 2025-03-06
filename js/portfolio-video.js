document.addEventListener("DOMContentLoaded", function () {
    var video = document.getElementById("portfolioVideo");
    var playButton = document.getElementById("playButton");

    // Define playVideo function
    window.playVideo = function () {
        if (video.paused) {
            video.play();
            playButton.style.display = "none"; // Hide button when playing
        } else {
            video.pause();
            playButton.style.display = "block"; // Show button when paused
        }
    };

    // Define jumpTo function for timeline buttons
    window.jumpTo = function (time) {
        if (video) {
            video.currentTime = time;
            video.play();
            playButton.style.display = "none"; // Hide play button on jump
        }
    };

    // Attach event listener to play button
    if (playButton) {
        playButton.addEventListener("click", playVideo);
    }
});
