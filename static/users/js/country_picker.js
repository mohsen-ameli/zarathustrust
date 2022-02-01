(function() {
    const all_countries = JSON.parse(document.getElementById('data').textContent);
    const NewCountryList = document.getElementById('new-country-list');
    const FormInput = document.getElementById('country-input');
    const form = document.getElementById('form')

    FormInput.addEventListener('keyup', e=>{
        form.addEventListener('submit', a=>{
            a.preventDefault()
        })
        var typed = e.target.value.toLowerCase()
        NewCountryList.innerHTML = ""
        let i=0

        if (e.target.value.length > 0 && typed != '') {
            for (const [key, value] of Object.entries(all_countries)) {
                if (value.startsWith(typed)){
                    i++
                    NewCountryList.innerHTML += `
                        <li>
                            <a class="dropdown-item" href="/register/personal/${key}" style="text-transform: capitalize;">
                                <span class="flag-icon flag-icon-${key.toLowerCase()} me-2"></span>${value}
                            </a>
                        </li>
                    `
                }
            }
            if (i <= 0) {
                NewCountryList.innerHTML = `
                    <li class="dropdown-item disabled" style="color: black;">
                        <b>No accounts were found.</b>
                    </li>
                `
            }
        } else {
            NewCountryList.innerHTML = `
                <li class="dropdown-item disabled" style="color: black;">
                    <b>No accounts were found.</b>
                </li>
            `
        }
    })
})();
