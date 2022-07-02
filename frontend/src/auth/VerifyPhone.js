import { useHistory, useLocation } from "react-router-dom";
import Otp from "../components/Otp";

const VerifyPhone = () => {
    const { state } = useLocation()
    let history = useHistory()

    if (!state?.fromVerifyEmail) {
        history.push("/country-picker")
    }

    return (
        <div className="verify-phone">
            <Otp url="/api/verify-phone/" next="/verify-referral" statePrev={state} stateNew={{"fromVerifyPhone": true}} translationTitle="verify_phone_title" translationHelp="phone_verify" />
        </div>
    );
}
 
export default VerifyPhone;