import Otp from "../components/Otp";

const VerifyPhone = () => {
    return (
        <div className="verify-phone">
            <Otp url="/api/verify-phone/" next="/verify-referral" translationTitle="verify_phone_title" translationHelp="phone_verify" />
        </div>
    );
}
 
export default VerifyPhone;