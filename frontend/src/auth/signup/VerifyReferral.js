import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useHistory, useLocation } from "react-router-dom";

import RotateLoader from 'react-spinners/RotateLoader';
import useMsgSwal from "../../components/useMsgSwal";

const VerifyReferral = () => {
    let { t }       = useTranslation()
    const { state } = useLocation()
    let history     = useHistory()

    const [isLoading, setIsLoading] = useState(false)
    const msgSwal                   = useMsgSwal()

    useEffect(() => {
        if (!state?.fromVerifyPhone) {
            history.push("/country-picker")
        }
        
        // eslint-disable-next-line
    }, [])

    let submit = async e => {
        setIsLoading(true)
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

            msgSwal(t(`${data.msg}`, {"username": String(data.user), "currency": data?.currency, "extraBonus": data?.extraBonus}), "success")
            history.push("/login")
        } else {
            msgSwal(t("register_error"), "error")
            setIsLoading(false)
        }
    }

    return (
        <div className="referral-code">
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("verify_referral")}</h3>
                    <hr className="zarathus-hr" />

                    <form onSubmit={e => submit(e)}>
                        <div className="form-floating">
                            <input type="text" className="form-control" name="code"
                            placeholder=" " id="id_referral_code" />

                            <label htmlFor="id_referral_code">{t("verify_referral")}</label>

                            <p className="form-text text-white">
                                {t("verify_referral_helper")}
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