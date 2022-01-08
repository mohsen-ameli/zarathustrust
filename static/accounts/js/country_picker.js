const FormInput = document.getElementById('country-input')
const FormList = document.getElementById('country-list');
const NewCountryList = document.getElementById('new-country-list')
const data = '{{ countries }}'
const countries = (data.replace(/&#x27;/g, '"').replace(/&quot;/g, '"'))
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
const rdata = JSON.parse("true")

const country_selector = (typed) => {
    $.ajax({
        type: 'POST',
        url:'/regiter/country_picker/',
        data : {
            'csrfmiddlewaretoken' : csrf,
            'typed' : typed,
        },
        success : (response) =>{
            const incoming = response.data
            if (Array.isArray(incoming)) {
                NewCountryList.innerHTML = ""
                incoming.forEach(country => {
                    NewCountryList.innerHTML += `
                    <li>
                        <a class="dropdown-item" href="/register/personal/${country[1]}" style="text-transform: capitalize;">
                            <span class="flag-icon flag-icon-${country[1].toLowerCase()} me-2"></span>${country[0]}
                        </a>
                    </li>
                    `
                })
            } else {
                NewCountryList.innerHTML = `
                <li class="dropdown-item disabled" style="color: black;">
                    <b>No countries were found.</b>
                </li>
                `
            }
        },
        error : (response) => {
            console.log("ERROR", response)
        }
    })
}

FormInput.addEventListener('keyup', e=>{
    FormList.style.display = 'none'
    country_selector(e.target.value)
})