(function() {
    const all_countries = JSON.parse(document.getElementById('data').textContent);
    const pk = JSON.parse(document.getElementById('pk').textContent);
    const NewCountryList = document.getElementById('new-country-list');
    const FormList = document.getElementById('country-list');
    const FormInput = document.getElementById('country-input');

    FormInput.addEventListener('keyup', e=>{
        NewCountryList.innerHTML = ""

        if (e.target.value.length > 0 && e.target.value != '') {
            FormList.style.display = 'none'

            for (const [key, value] of Object.entries(all_countries)) {
                if (value.startsWith(e.target.value)){
                    console.log(value.startsWith(e.target.value).length)
                    NewCountryList.innerHTML += `
                        <li>
                            <a class="dropdown-item" href="/${pk}/settings/country/${key}" style="text-transform: capitalize;">
                                <span class="flag-icon flag-icon-${key.toLowerCase()} me-2"></span>${value}
                            </a>
                        </li>
                    `
                }
            }
        } else {
            NewCountryList.innerHTML = `
                <li class="dropdown-item disabled" style="color: black;">
                    <b>No countries were found.</b>
                </li>
            `
        }
    })
})();