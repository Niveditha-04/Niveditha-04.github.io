document.addEventListener("DOMContentLoaded", function () {
    var video = document.getElementById("portfolioVideo");
    var playButton = document.getElementById("playButton");

    // Make playVideo globally accessible
    window.playVideo = function () {
        if (video.paused) {
            video.play();
            playButton.style.display = "none";
        } else {
            video.pause();
            playButton.style.display = "block";
        }
    };

    // Make jumpTo globally accessible
    window.jumpTo = function (time) {
        if (video) {
            video.currentTime = time;
            video.play();
            playButton.style.display = "none";
        }
    };

    // Attach event listener to play button
    if (playButton) {
        playButton.addEventListener("click", playVideo);
    }

    console.log("Portfolio Video JS Loaded Successfully");
});

