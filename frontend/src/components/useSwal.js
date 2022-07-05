import { useTranslation } from 'react-i18next'
import Swal from 'sweetalert2'

const useSwal = ( text, submit ) => {
    let { t } = useTranslation()

    let confirm = () => {
        Swal.fire({
            // title: "Confirm actions ?",
            text: text,
            icon: "warning",
            width: "20rem",
            buttonsStyling: "false",
            showCancelButton: true,
            confirmButtonText: t("confirm"),
            cancelButtonText: t("cancel"),
            // showClass: {
            //     popup: "animate__animated animate__zoomInDown",
            //     },
            //     hideClass: {
            //     popup: "animate__animated animate__zoomOutDown",
            //     },
        })
        .then(result => {
            if (result.isConfirmed) {
                submit()
            }
        })
    }

    return (confirm)
}
 
export default useSwal;