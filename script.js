(function () {
    var INTERVAL = 7000; // 7 seconds

    var gallery = document.querySelector('.gallery');
    var swapped = false;

    setInterval(function () {
        swapped = !swapped;
        gallery.classList.toggle('swapped', swapped);
    }, INTERVAL);
})();
