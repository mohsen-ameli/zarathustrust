(function() {
    // django vars
    const person = JSON.parse(document.getElementById('reciever_name').textContent);
    const minCurrency = JSON.parse(document.getElementById('min_currency').textContent);
    const userCurrencySymbol = JSON.parse(document.getElementById('user_currency_symbol').textContent);

    // amount to send section vars
    const form = document.querySelector("#form-swal")
    const parentDiv = document.querySelector('#div_id_money_to_send')
    const input = document.querySelector("#id_money_to_send")
    const submitBtn = document.querySelector("#Action")

    // message section vars
    const parentMsgDiv = document.querySelector("#div_id_purpose")
    const msgCounter = document.querySelector("#msgCounter")
    const msgInput = document.querySelector("#id_purpose")
    var max = 200
    var healthy = true


    // creating the first div for minimum amount error
    let div = document.createElement("div")
    div.classList.add("invalid-feedback")
    div.classList.add("my-2")
    div.style.display = "none"
    let divText = document.createTextNode(`Please consider that the minimum amount to send is ${userCurrencySymbol}${minCurrency} !`)
    div.appendChild(divText)

    // creating the second div for not a number error
    let div2 = document.createElement("div")
    div2.classList.add("invalid-feedback")
    div2.classList.add("my-2")
    div2.style.display = "none"
    let div2Text = document.createTextNode('Please enter a number !')
    div2.appendChild(div2Text)

    // creating the third div to check to see if maximum number of characters were entered
    let div3 = document.createElement("div")
    div3.classList.add("invalid-feedback")
    div3.classList.add("my-2")
    div3.style.display = "none"

    // appending the three sections to their parent div
    parentDiv.appendChild(div)
    parentDiv.appendChild(div2)
    parentMsgDiv.appendChild(div3)

    // whether the user submited something or not
    document.querySelector("#form-swal").addEventListener('submit', a=>{
        a.preventDefault();
        if (good == true && healthy == true) {
            var spin = document.querySelector("#spinnner");
            var price = document.querySelector("#form-swal").elements[2].value;

            Swal.fire({
                title: "Confirm actions ?",
                text: `You are about to send ${userCurrencySymbol}${price} to ${person}`,
                icon: "warning",
                width: "20rem",
                cancelButtonText: "Change",
                buttonsStyling: "false",
                showClass: {
                    popup: "animate__animated animate__zoomInDown",
                },
                hideClass: {
                    popup: "animate__animated animate__zoomOutDown",
                },
                showCancelButton: true,
                background: "#ffffffff",
                confirmButtonText: "Transfer",
            }).then((result) => {
                if (result.isConfirmed) {
                    spin.innerHTML =
                        '<div class="spinner"><div id="container" class="spinner-class"><svg viewBox="0 0 100 100"><defs><filter id="shadow"><feDropShadow dx="0" dy="0" stdDeviation="1.5" flood-color="#fc6767"/></filter></defs><circle id="spinner" cx="50" cy="50" r="45"/></svg></div></div>';
                    setTimeout(() => {
                        form.submit();
                    }, 500);
                }
            });
        }
    })

    // live error check for amount to send
    input.addEventListener('keyup', e=>{
        let money = e.target.value

        if (money < minCurrency && money != "") { // user entered value below min point
            div.style.display = ""
            div2.style.display = "none"
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

    // live error check for message length
    msgInput.addEventListener('keyup', e=>{
        let len = e.target.value.length

        if (len <= max) { // if characters entered were less than maximum
            healthy = true
            msgInput.classList.remove("is-invalid")
            if (len == 0){ // if the number of characters entered counted 0
                msgCounter.style.display = "none"
            } else { // normal behaviour
                if (len >= max * 0.75){
                    msgCounter.style.display = ""
                    msgCounter.innerHTML = `<div>Maximum characters (${len}/${max})<div/>`
                    document.querySelector("#msgCounter > div").style.color = "orange"
                } else {
                    msgCounter.style.display = ""
                    msgCounter.innerHTML = `<div>Maximum characters (${len}/${max})<div/>`
                }
            }
        } else { // limit reached
            div3.innerHTML = `<div>Maximum number of characters reached ! (${-len+max})<div/>`
            msgCounter.style.display = "none"
            div3.style.display = ""
            msgInput.classList.add("is-invalid")
            healthy = false
        }
    })
})();