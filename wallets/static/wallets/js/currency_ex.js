(function() {
    const currency_options = JSON.parse(document.getElementById("currency_options").textContent)

    var to_currency_list = currency_options
    const input = document.getElementById("floatingInput")
    const fromDropdownMenu = document.getElementById("fromDropdownMenu")
    const toDropdownMenu = document.getElementById("toDropdownMenu")
    const form = document.getElementById("form-post")
    const from_dropdown_items = document.querySelector("#dropdown-from-item")
    const to_dropdown_items = document.querySelector("#dropdown-to-item")
    const parentDiv = document.querySelector('#parent-div')

    var minCurrency = 1
    var post = false
    var currency_symbol = ""
    var currency_min = ""


    // creating the first div for minimum amount error
    let div = document.createElement("div")
    div.classList.add("invalid-feedback")
    div.classList.add("my-2")
    div.classList.add("position-absolute")
    div.style.display = "none"
    // let divText = document.createTextNode(`Please consider that the minimum amount to send is !`)
    // div.appendChild(divText)

    // creating the second div for not a number error
    let div2 = document.createElement("div")
    div2.classList.add("invalid-feedback")
    div2.classList.add("my-2")
    div2.classList.add("position-absolute")
    div2.style.display = "none"
    let div2Text = document.createTextNode('Please enter a number !')
    div2.appendChild(div2Text)

    // appending the three sections to their parent div
    parentDiv.appendChild(div)
    parentDiv.appendChild(div2)


    // initial to_selection_dropdown
    to_currency_list.forEach(item => {
        if (item[0] != currency_options[0][0]) {
            to_dropdown_items.style = ""
            to_dropdown_items.innerHTML += `
                <li><a class="dropdown-item" href="#">${item[0]} (${item[1]})</a></li>
            `
        }
    })
    toDropdownMenu.innerHTML = `${to_currency_list[1][0]} (${to_currency_list[1][1]})`

    // the from_currency dropdown event listener
    from_dropdown_items.addEventListener("click", e=>{
        var selected = e.target.text
        fromDropdownMenu.innerText = selected
        to_dropdown_items.innerHTML = ""
        to_currency_list = JSON.parse(document.getElementById("currency_options").textContent)

        currency_options.forEach(currency => { // looping through our options
            if (currency[0] + " (" + currency[1] + ")" == selected) { // the currency has been selected
                var index = currency_options.indexOf(currency)
                to_currency_list.splice(index, 1) // removing the selected item from our currency list
            }
        });

        to_currency_list.forEach(item => {
            to_dropdown_items.style = ""
            to_dropdown_items.innerHTML += `
                <li><a class="dropdown-item" href="#">${item[0]} (${item[1]})</a></li>
            `
        })
        toDropdownMenu.innerHTML = `${to_currency_list[0][0]} (${to_currency_list[0][1]})`
    })

    // amount input listener
    input.addEventListener("keyup", e=>{
        typed = e.target.value

        // getting our min values and filling in our invalid div 
        // error message with proper symbols and values
        var from_currency = fromDropdownMenu.innerText.split(" ")[0]
        currency_options.forEach(currency => {
            if (currency[0] == from_currency) {
                currency_symbol = currency[1]
                minCurrency = currency[2]
                div.innerText = `Please consider that the minimum amount to send is ${currency_symbol}${minCurrency} !`
            }
        })

        if (typed.length > 0 && typed != "") {
            if (typed < minCurrency){ // user inputed an amount less than the min value
                input.classList.add("is-invalid")
                div.style.display = ""
                div2.style.display = "none"
                post = false;
            } else if (isNaN(typed) == true){ // user inputed characters
                input.classList.add("is-invalid")
                div.style.display = "none"
                div2.style.display = ""
                post = false;
            } else {
                input.classList.remove("is-invalid")
                post = true;
            }
        } else {
            input.classList.remove("is-invalid")
        }
    })

    // the to_currency dropdown event listener
    to_dropdown_items.addEventListener("click", e=>{
        var selected = e.target.text
        toDropdownMenu.innerHTML = selected
    })

    // listening for user submit
    form.addEventListener("submit", e=>{
        e.preventDefault()
        if (post == true) {
            var amount        = input.value
            var to_currency   = toDropdownMenu.innerText.split(" ")[0]
            var from_currency = fromDropdownMenu.innerText.split(" ")[0]

            window.location = `${from_currency}/${amount}/${to_currency}`
        }
    })

})();

