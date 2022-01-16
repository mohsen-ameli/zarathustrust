const url = window.location.href
const searchInput = document.getElementById('search-input')
const searchForm = document.getElementById('search-form')
const resultsBox = document.getElementById('results-box')
const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
const sendSearchData = (typed) => {
    $.ajax ({
        type: 'POST',
        url: '/transfer_search/search_results/',
        data: {
            'csrfmiddlewaretoken' : csrf,
            'person': typed,
        },
        success: (response) => {
            const result = response.data
            if (Array.isArray(result)) { // we found accounts
                resultsBox.innerHTML = ""
                result.forEach(person=>{
                    resultsBox.innerHTML += `
                    <li>
                        <a class="dropdown-item" href="${person.username}" style="text-transform: capitalize;">
                        ${person.username}
                        </a>
                    </li>
                `
                })
            } else { // we didn't find any accounts
                if (searchInput.value.length > 0) {
                    resultsBox.innerHTML = `
                        <li>
                            <a class="dropdown-item disabled" style="text-transform: capitalize; color: black;">
                                <b>${result}</b>
                            </a>
                        </li>
                    `
                } else {
                    resultsBox.classList.add('not-visible')
                }
            }
        },
        error: (response) => {
            console.log(response)
        },
    })
}

searchInput.addEventListener('keyup', e=>{
    if (resultsBox.classList.contains('not-visible')) {
        resultsBox.classList.remove('not-visible')
    }
    if (e.target.value.length >= 5){
        sendSearchData(e.target.value)
    } else {
        resultsBox.innerHTML = `
            <li>
                <a class="dropdown-item disabled" style="text-transform: capitalize; color: black;">
                    <b>{% trans "No accounts were found." %}</b>
                </a>
            </li>
        `
    }
})