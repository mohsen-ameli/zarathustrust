(function() {
    // amount to send section vars
    const minCurrency = JSON.parse(document.getElementById('min_currency').textContent);
    const userCurrencySymbol = JSON.parse(document.getElementById('user_currency_symbol').textContent);
    const form = document.querySelector("#deposit-form")
    const parentDiv = document.querySelector('#div_id_add_money')
    const input = document.querySelector("#id_add_money")
    const submitBtn = document.querySelector("#Action")

    // creating the first div for minimum amount error
    let div = document.createElement("div")
    div.classList.add("invalid-feedback")
    div.classList.add("mt-2")
    div.style.display = "none"
    let divText = document.createTextNode(`Please consider that the minimum amount to send is ${userCurrencySymbol}${minCurrency} !`)
    div.appendChild(divText)

    // creating the second div for not a number error
    let div2 = document.createElement("div")
    div2.classList.add("invalid-feedback")
    div2.classList.add("mt-2")
    div2.style.display = "none"
    let div2Text = document.createTextNode('Please enter a number !')
    div2.appendChild(div2Text)

    // appending the three sections to their parent div
    parentDiv.appendChild(div)
    parentDiv.appendChild(div2)

    // whether the user submited something or not
    form.addEventListener('submit', a=>{
        a.preventDefault();
        if (good == true) {
            form.submit()
        }
    })

    // live error check for amount to send
    input.addEventListener('keyup', e=>{
        let money = e.target.value

        if (money < minCurrency && money != "") { // user entered value below min point
            div.style.display = ""
            input.classList.add("is-invalid")
            good = false
        } else if (isNaN(money) == true) { // user entered characters instead of numbers
            div.style.display = "none"
            div2.style.display = ""
            input.classList.add("is-invalid")
            good = false
        } else { // valid
            input.classList.remove("is-invalid")
            div.style.display = "none"
            div2.style.display = "none"
            submitBtn.style.display = ""
            good = true
        }
    })
})();