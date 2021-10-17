/* window.onload = function () {
    var total_bal = 100;
    ctr = document.getElementById("counter");
    function incrementCounter() {
        ctr.innerHTML = total_bal;
        new_bal = total_bal * 0.01 / 31104000; //* 0.0000001585
        total_bal = new_bal + total_bal;
        if (total_bal < Infinity)
            setTimeout(incrementCounter, 50);
    }
    incrementCounter();
} */
/* window.onload = function () {
    var total_bal = Number('{{ object.total_balance }}');
    ctr = document.getElementById("counter");
    function incrementCounter() {
        ctr.innerHTML = total_bal;
        new_bal = total_bal * 0.01 / 31104000; //* 0.0000001585
        total_bal = new_bal + total_bal;
        if (total_bal < Infinity)
            setTimeout(incrementCounter, 50);
    }
    incrementCounter();
} */
/* var ctr = document.getElementById("new-counter");
var hi = Number('{{ object.total_balance }}');
ctr.innerHTML = hi */