import { useLocation } from "react-router-dom";
import Otp from "../../components/Otp";

const VerifyVerify = () => {
    const { state } = useLocation()

    return (
        <div className="verify-email">
            <Otp url="/api/verify-email/" next="/verify-phone" statePrev={state} stateNew={{"fromVerifyEmail": true, "msg": "phone_verify"}} translationTitle="verify_email_title" translationHelp="email_verify" />
        </div>
    );
}
 
export default VerifyVerify;