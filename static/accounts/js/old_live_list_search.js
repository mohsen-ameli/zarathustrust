(function() {
    const rdata = JSON.parse(data.replace(/&quot;/g, '"'))
    const input = document.getElementById("search_here")
    const box = document.getElementById("box")

    let filterArr = []
    input.addEventListener('keyup', (e)=>{
        box.innerHTML = ""
        if (e.target.value != '' && e.target.value.length >= 3) {
            filterArr = rdata.filter(info => info['username'].includes(e.target.value))
            if (filterArr.length > 0) {
                filterArr.map(item => {
                    box.innerHTML += `
                    <button class="list-group-item list-group-item-action list-group-item-light" type="submit" name="search_result" 
                    value="${item['username']}">${item['username']}</button>
                `
                })
            } else {
                box.innerHTML = `<a href="#" class="list-group-item list-group-item-action list-group-item-light disabled">
                    No accounts were found, try entering their email or phone number, or check your spelling.</a>`
            }
        } else {
            box.innerHTML = `<a href="#" class="list-group-item list-group-item-action list-group-item-light disabled">
                No accounts were found, try entering their email or phone number, or check your spelling.</a>`
        }
    })
})();