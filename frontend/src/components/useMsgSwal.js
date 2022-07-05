import { useTranslation } from 'react-i18next'
import Swal from 'sweetalert2'
import withReactContent from 'sweetalert2-react-content'

const useMsgSwal = () => {
    const MySwal = withReactContent(Swal)
    let { t } = useTranslation()

    let run = (message, variant) => MySwal.fire({
        title: message,
        icon: variant,
        confirmButtonText: t('confirm')
      })

    return run
}
 
export default useMsgSwal;