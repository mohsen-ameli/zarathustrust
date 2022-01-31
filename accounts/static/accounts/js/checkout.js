(function() {
  const price = JSON.parse(document.getElementById('price').textContent);
  document.querySelector("#form-swal").addEventListener("submit", function (e) {
    var spin = document.querySelector("#spinnner");
    var form = this;
    e.preventDefault();

    Swal.fire({
      title: "Confirm actions ?",
      text: `You are about to pay $${price}`,
      icon: "warning",
      width: "20rem",
      buttonsStyling: "false",
      showClass: {
        popup: "animate__animated animate__zoomInDown",
      },
      hideClass: {
        popup: "animate__animated animate__zoomOutDown",
      },
      showCancelButton: true,
      background: "#ffffffff",
      confirmButtonText: "Place Order",
    }).then((result) => {
      if (result.isConfirmed) {
        spin.innerHTML =
          '<div class="spinner"><div id="container" class="spinner-class"><svg viewBox="0 0 100 100"><defs><filter id="shadow"><feDropShadow dx="0" dy="0" stdDeviation="1.5" flood-color="#fc6767"/></filter></defs><circle id="spinner" cx="50" cy="50" r="45"/></svg></div></div>';
        setTimeout(() => {
          form.submit();
        }, 500);
      }
    });
  });
})();