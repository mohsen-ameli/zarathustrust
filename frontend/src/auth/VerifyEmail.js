import Otp from "../components/Otp";

const VerifyVerify = () => {
    return (
        <div className="verify-email">
            <Otp url="/api/verify-email/" next="/verify-phone" translationTitle="verify_email_title" translationHelp="email_verify" />
        </div>
    );
}
 
export default VerifyVerify;