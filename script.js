(function () {
    var shots = document.querySelectorAll('.shot');
    var current = 0;

    setInterval(function () {
        shots[current].classList.remove('is-active');
        current = (current + 1) % shots.length;
        shots[current].classList.add('is-active');
    }, 7000);
})();
