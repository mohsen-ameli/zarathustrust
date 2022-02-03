(function() {
    const data = JSON.parse(document.getElementById('data').textContent)
    const pk = JSON.parse(document.getElementById('pk').textContent)
    const NewCountryList = document.getElementById('new-country-list')
    const FormInput = document.getElementById('country-input')

    FormInput.addEventListener('keyup', e=>{
        var typed = e.target.value.toUpperCase()
        NewCountryList.innerHTML = ""

        if (e.target.value.length > 0 && typed != '') {
            var i=0
            for (const [key, value] of Object.entries(data)) {
                if (value.startsWith(typed)){
                    i++
                    NewCountryList.innerHTML += `
                        <li>
                            <a class="dropdown-item" href="/${pk}/new_wallet/${value}/" style="text-transform: capitalize;">
                                <span class="flag-icon flag-icon-${key.toLowerCase()} me-2"></span>${value}
                            </a>
                        </li>
                    `
                }
            }
            if (i <= 0) {
                NewCountryList.innerHTML = `
                    <li class="dropdown-item disabled" style="color: black;">
                        <b>No currencies were found.</b>
                    </li>
                `
            }
        } else {
            NewCountryList.innerHTML = `
                <li class="dropdown-item disabled" style="color: black;">
                    <b>Search for your desired currency</b>
                </li>
            `
        }
    })
})();