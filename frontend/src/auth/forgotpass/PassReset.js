import { useState } from "react"
import { useTranslation } from "react-i18next"
import RotateLoader from 'react-spinners/RotateLoader'
import MsgAlert from "../../components/MsgAlert"

const PassReset = () => {
    const [success, setSuccess] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [err, setErr] = useState(false)

    let { t } = useTranslation()

    let submit = async e => {
        e.preventDefault()
        setIsLoading(true)

        let res = await fetch("/api/password-reset/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "email": e.target.email.value
            })
        })

        if (res.ok) {
            setSuccess(true)
            setIsLoading(false)
        } else {
            setIsLoading(false)
            setErr("no_user_email")
        }
    }


    return (
        <div className="pass-reset">
            {err && <MsgAlert msg={t(err)} variant="danger" />}

            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            {!success ? 
                <div className="card text-white zarathus-card mx-auto">
                    <div className="card-body">
                        <form onSubmit={e => submit(e)}>
                            <h3 className="fw-normal text-center">{t("reset_pass")}</h3>
                            <hr className="zarathus-hr" />

                            <div id="div_id_email" className="form-group form-floating mb-3">
                                <input type="email" name="email" autoComplete="home email" maxLength="254" className="form-control" 
                                required={true} id="email" placeholder=" " />

                                <label htmlFor="email">{t("email")}</label>
                            </div>
                            <button className="neon-button-green my-2" type="submit">{t("request_pass_reset")}</button>
                        </form>
                    </div>
                </div>
            :
            <MsgAlert msg={t("email_reset_msg")} variant="primary" />
            }
        </div>
    );
}
 
export default PassReset;