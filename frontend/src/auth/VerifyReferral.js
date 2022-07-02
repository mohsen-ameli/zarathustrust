import { useTranslation } from "react-i18next";
import { useHistory, useLocation } from "react-router-dom";

const VerifyReferral = () => {
    let { t } = useTranslation()
    const { state } = useLocation()
    let history = useHistory()
    
    if (!state?.fromVerifyPhone) {
        history.push("/country-picker")
    }

    let submit = async e => {
        e.preventDefault()
        
        let res = await fetch("/api/verify-referral/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "code": e.target.code.value
            })
        })

        if (res.ok) {
            let data = await res.json()
            localStorage.setItem("success", true)
            localStorage.setItem("msg", data.msg)
            history.push("/login")
        } else {
            localStorage.setItem("success", false)
            localStorage.setItem("msg", "An error occured while registering. Please try again later.")
        }
    }

    return (
        <div className="referral-code">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">Referral Code (Optional)</h3>
                    <hr className="zarathus-hr" />

                    <form onSubmit={e => submit(e)}>
                        <div className="form-floating">
                            <input type="text" className="form-control" name="code"
                            placeholder=" " id="id_referral_code" />

                            <label htmlFor="id_referral_code">Referral Code (Optional)</label>

                            <p className="form-text text-white">
                                Please enter your referral code to get grand prizes , or leave blank for no prize!
                            </p>
                        </div>

                        <button className="neon-button-green my-2" type="submit">{t("verify")}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
 
export default VerifyReferral;