document.addEventListener("DOMContentLoaded", function () {
    var video = document.getElementById("portfolioVideo");
    var playButton = document.getElementById("playButton");

    // Debugging: Check if elements are found
    if (!video) {
        console.error("❌ Video element not found!");
    }
    if (!playButton) {
        console.error("❌ Play button not found!");
    }

    // Define playVideo function globally
    window.playVideo = function () {
        if (video.paused) {
            video.play();
            playButton.style.display = "none"; // Hide play button when playing
        } else {
            video.pause();
            playButton.style.display = "block"; // Show play button when paused
        }
    };

    // Define jumpTo function globally
    window.jumpTo = function (time) {
        if (video) {
            video.currentTime = time;
            video.play();
            playButton.style.display = "none"; // Hide play button when jumping
        }
    };

    // Attach event listener to play button
    if (playButton) {
        playButton.addEventListener("click", playVideo);
    }
});


