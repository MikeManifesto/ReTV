(function () {
    var INTERVAL = 7000; // 7 seconds per slide

    var slides = document.querySelectorAll('.slide');
    var dots   = document.querySelectorAll('.dot');
    var current = 0;
    var timer   = null;

    function show(index) {
        slides[current].classList.remove('is-active');
        dots[current].classList.remove('is-active');

        current = (index + slides.length) % slides.length;

        slides[current].classList.add('is-active');
        dots[current].classList.add('is-active');
    }

    function next() {
        show(current + 1);
    }

    function startTimer() {
        clearInterval(timer);
        timer = setInterval(next, INTERVAL);
    }

    dots.forEach(function (dot, i) {
        dot.addEventListener('click', function () {
            show(i);
            startTimer();
        });
    });

    startTimer();
})();
