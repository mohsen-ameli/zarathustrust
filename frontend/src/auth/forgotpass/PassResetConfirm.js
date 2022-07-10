import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useHistory, useParams } from "react-router-dom";

import useMsgSwal from "../../components/useMsgSwal";

const PassResetConfirm = () => {
    const [err, setErr] = useState(null)
    const [ok, setOk]   = useState(false)
    const msgSwal       = useMsgSwal()

    let { t } = useTranslation()
    let history = useHistory()

    const uidb64 = useParams().uidb64
    const token = useParams().token
    
    useEffect(() => {
        let verifyCreds = async () => {
            let res = await fetch(`/api/password-reset-confirm/${uidb64}/${token}/`)

            if (res.ok) {
                let data = await res.json()
                
                if (data.success) {
                    setOk(true)
                }
            } else {
                // token has expired or has been tampered with
                history.push("/password-reset")
            }

        }; verifyCreds()
        // eslint-disable-next-line
    }, [])

    let submit = async e => {
        e.preventDefault()

        if (e.target.password.value !== e.target.password2.value) {
            setErr(t("pass_no_match"))
        } else if (ok) {
            let res = await fetch("/api/password-reset-complete/", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "password": e.target.password.value,
                    "uidb64": uidb64,
                    "token": token
                })
            })
    
            if (res.ok) {
                msgSwal(t("pass_success_change"), "success")
                history.push("/login")
            } else {
                msgSwal(t("pass_unsuccess_change"), "error")
                history.push("/password-reset")
            }
        } else {
            msgSwal(t("pass_unsuccess_change"), "error")
            history.push("/password-reset")
        }
    }

    return (
        <div className="pass-reset-confirm">
            <div className="card text-white zarathus-card mx-auto my-3">
                <div className="card-body">
                    <form onSubmit={e => submit(e)} autoComplete="off">
                        <h3 className="fw-normal text-center">{t("reset_pass")}</h3>
                        <hr className="zarathus-hr" />

                        {/* Password */}
                            <div className="form-floating">
                            <input type="password" className="form-control" required={true}
                            placeholder=" " id="password" name="password"/>

                            <label htmlFor="password">{t("password")}</label>

                            <span className="invalid-feedback"><strong>
                                
                            </strong></span>

                            <ul className="form-text text-white">
                                {t("password_help").split("\\n").map((item, key) => (
                                    <li key={key}>{item}</li>
                                ))}
                            </ul>
                        </div>

                        {/* Password confirm */}
                        <div className="form-floating"> 
                            <input type="password" className={err ? "form-control is-invalid" : "form-control"} required={true}
                            placeholder=" " id="password2" />

                            <label htmlFor="password-confirm">{t("password_confirm")}</label>

                            <span className="invalid-feedback"><strong>
                                {err && err}
                            </strong></span>

                            <p className="form-text text-white">
                                {t("password_confirm_help")}
                            </p>
                        </div>

                        {/* submit */}
                        <button className="neon-button-green my-2">{t("change_pass")}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
 
export default PassResetConfirm;