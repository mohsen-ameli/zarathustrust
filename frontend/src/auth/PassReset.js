import { useState, useRef } from "react"
import { useTranslation } from "react-i18next"
import Alert from 'react-bootstrap/Alert'
import RotateLoader from 'react-spinners/RotateLoader'

const PassReset = () => {
    const [success, setSuccess] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    let { t } = useTranslation()
    let ref = useRef()

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
            console.log("unssuccess", res)
        }
    }


    let dismiss = () => {
        const element = ref.current
        element.classList.replace("animate__fadeInDown", "animate__fadeOutDown")
    }


    return (
        <div className="pass-reset">
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            {!success ? 
                <div className="card text-white zarathus-card mx-auto">
                    <div className="card-body">
                        <form onSubmit={e => submit(e)}>
                            <h3 className="fw-normal text-center">Reset Your Password</h3>
                            <hr className="zarathus-hr" />

                            <div id="div_id_email" className="form-group form-floating mb-3">
                                <input type="email" name="email" autoComplete="home email" maxLength="254" className="form-control" 
                                required={true} id="email" placeholder=" " />

                                <label htmlFor="email">Email</label>
                            </div>
                            <button className="neon-button-green my-2" type="submit">Request Password Reset</button>
                        </form>
                    </div>
                </div>
            :
            <Alert className="text-center animate__animated animate__fadeInDown"
                variant="primary" onClick={() => dismiss()} dismissible ref={ref}>
                { t("email_reset_msg") }
            </Alert>
            }
        </div>
    );
}
 
export default PassReset;