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
                    <a href="${person.username}" class="list-group-item list-group-item-action list-group-item-light">
                    <b>${person.username}</b>
                    </a>`
                })
            } else { // we didn't find any accounts
                if (searchInput.value.length > 0) {
                    resultsBox.innerHTML = `<div class="list-group-item"><b>${result}</b></div>`
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
        resultsBox.innerHTML = `<div class="list-group-item"><b>No accounts were found.</b></div>`
    }
})