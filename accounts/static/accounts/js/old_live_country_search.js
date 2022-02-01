(function() {
    const pk = JSON.parse(document.getElementById('pk').textContent);
    const default_country = JSON.parse(document.getElementById('default_country').textContent);

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
                if (Array.isArray(incoming)) { // if response is an array
                    incoming.forEach(country => {
                        if (country[0].startsWith(typed)) {
                            NewCountryList.innerHTML += `
                            <li>
                                <a class="dropdown-item" href="/${pk}/settings/country/${country[1]}" style="text-transform: capitalize;">
                                    <span class="flag-icon flag-icon-${country[1].toLowerCase()} me-2"></span>${country[0]}
                                </a>
                            </li>
                            `
                        }
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
        NewCountryList.innerHTML = ""
        if (e.target.value.length > 0 && e.target.value != '') {
            FormList.style.display = 'none'
            country_selector(e.target.value)
        } else {
            NewCountryList.innerHTML = `
                <li class="dropdown-item disabled" style="color: black;">
                    <b>No countries were found.</b>
                </li>
            `
        }
    })
})();