import { useHistory, useLocation } from "react-router-dom";
import Otp from "../components/Otp";

const VerifyVerify = () => {
    const { state } = useLocation()
    let history = useHistory()
    
    if (!state?.fromSignUp) {
        history.push("/country-picker")
    }

    return (
        <div className="verify-email">
            <Otp url="/api/verify-email/" next="/verify-phone" state={{"fromVerifyEmail": true}} translationTitle="verify_email_title" translationHelp="email_verify" />
        </div>
    );
}
 
export default VerifyVerify;