(function() {
    var total_bal = Number(JSON.parse(document.getElementById('total_bal').textContent));
    var interest_rate = Number(JSON.parse(document.getElementById('interest_rate').textContent));

    window.onload = function () {
        ctr = document.getElementById("counter");
        function incrementCounter() {
            ctr.innerHTML = interest_rate.toFixed(20);

            /* one percent of the total balance per second */
            interest = total_bal * 0.01 / 31536000
            interest_rate = interest_rate + interest;

            /* timeout every second */
            setTimeout(incrementCounter, 1000);
        }
        if (total_bal > 0){
            /* loopdy loop back up untill infinity */
            incrementCounter();
        } else {
            ctr.innerHTML = "0.00000000000000000000";
        }
    }
})();
