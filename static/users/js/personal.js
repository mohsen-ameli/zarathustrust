(function() {
    const ext = JSON.parse(document.getElementById('ext').textContent);
    const ext_obj = document.getElementById("phone_ext");

    ext_obj.innerHTML = `+(${ext})`
})();