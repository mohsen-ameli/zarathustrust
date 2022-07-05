import { useRef } from 'react'
import Alert from 'react-bootstrap/Alert'

const MsgAlert = ({ msg, variant }) => {
    let ref = useRef()
    
    let dismiss = () => {
        const element = ref.current
        element.classList.replace("animate__fadeInDown", "animate__fadeOutDown")
        setTimeout(() => element.style.display = "none", 1000)
    }

    return (
        <div className="msg-alert">
            <Alert className="text-center animate__animated animate__fadeInDown"
            variant={variant} onClose={() => dismiss()} dismissible ref={ref}>
                { msg }
            </Alert>
        </div>
    );
}
 
export default MsgAlert;