    var video = document.getElementById("portfolioVideo");
function playVideo() {
        if (video.paused) {
            video.play();
            playButton.style.display = "none"; // Hide play button when playing
        } else {
            video.pause();
            playButton.style.display = "block"; // Show play button when paused
        }
    }

document.addEventListener("DOMContentLoaded", function () {
    var playButton = document.getElementById("playButton");

    video.addEventListener("click",function() {
            playVideo();
    })

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
        playButton.addEventListener("click", playVideo);
    }
});

// Function for Jumping to Timestamps
function jumpTo(time) {
    var video = document.getElementById("portfolioVideo");
    if (video) {
        video.currentTime = time;
        video.play();
        document.getElementById("playButton").style.display = "none"; // Hide play button when jumping
    }
}


