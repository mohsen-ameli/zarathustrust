document.querySelector("#Action").addEventListener("click", function() {
    document.querySelector('#form-swal').addEventListener('submit', function(e) {
        var spin = document.querySelector("#spinnner")
        var price = document.querySelector("#form-swal").elements[1].value
        var form = this;
        e.preventDefault();
    
        Swal.fire({
            title: 'Confirm actions ?',
            text: `You are about to withdraw $${price}`,
            icon: 'warning',
            width: "20rem",
            cancelButtonText: "Change",
            buttonsStyling: "false",
            showClass: {
              popup: 'animate__animated animate__zoomInDown'
            },
            hideClass: {
              popup: 'animate__animated animate__zoomOutDown'
            },
            showCancelButton: true,
            background: '#ffffffff',
            confirmButtonText: 'Withdraw'
          }).then((result) => {
            if (result.isConfirmed) {
                spin.innerHTML = '<div class="spinner"><div id="container" class="spinner-class"><svg viewBox="0 0 100 100"><defs><filter id="shadow"><feDropShadow dx="0" dy="0" stdDeviation="1.5" flood-color="#fc6767"/></filter></defs><circle id="spinner" cx="50" cy="50" r="45"/></svg></div></div>'
                setTimeout(() => { form.submit(); }, 500);
            }
          })
    
    });
}) 

