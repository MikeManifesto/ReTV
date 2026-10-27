(function () {
    var shots = document.querySelectorAll('.shot');
    var dotsBox = document.querySelector('.dots');
    var current = 0;
    var timer;

    var dots = [];
    for (var i = 0; i < shots.length; i++) {
        (function (index) {
            var d = document.createElement('button');
            d.type = 'button';
            d.className = 'dot' + (index === 0 ? ' is-active' : '');
            d.setAttribute('aria-label', 'Show screenshot ' + (index + 1));
            d.addEventListener('click', function () {
                show(index);
                restart();
            });
            dotsBox.appendChild(d);
            dots.push(d);
        })(i);
    }

    function show(next) {
        shots[current].classList.remove('is-active');
        dots[current].classList.remove('is-active');
        current = next;
        shots[current].classList.add('is-active');
        dots[current].classList.add('is-active');
    }

    function restart() {
        clearInterval(timer);
        timer = setInterval(function () {
            show((current + 1) % shots.length);
        }, 10000);
    }

    restart();
})();
