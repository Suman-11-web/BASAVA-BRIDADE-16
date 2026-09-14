document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Premium Countdown Timer Logic
    const countdownContainer = document.getElementById("countdown");
    
    // ONLY run the timer if the countdown element actually exists on the page
    if (countdownContainer) {
        
        // Target Date: September 4, 2027 at 08:00 AM
        const targetDate = new Date("Sep 04, 2027 08:00:00").getTime();

        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = targetDate - now;

            // If the countdown is finished
            if (distance < 0) {
                countdownContainer.innerHTML = "<div class='text-gold text-2xl md:text-3xl font-bold animate-pulse w-full text-center'>The 2027 Festival is Live!</div>";
                return;
            }

            // Calculate time left
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Safely grab the DOM elements
            const daysEl = document.getElementById("days");
            const hoursEl = document.getElementById("hours");
            const minutesEl = document.getElementById("minutes");
            const secondsEl = document.getElementById("seconds");

            // Update DOM with padded zeros (e.g., "09" instead of "9")
            if (daysEl) daysEl.innerText = String(days).padStart(2, '0');
            if (hoursEl) hoursEl.innerText = String(hours).padStart(2, '0');
            if (minutesEl) minutesEl.innerText = String(minutes).padStart(2, '0');
            if (secondsEl) secondsEl.innerText = String(seconds).padStart(2, '0');
        };

        // Run it once immediately to avoid the 1-second blank flash
        updateCountdown();
        
        // Update every 1 second
        setInterval(updateCountdown, 1000);
    }
});