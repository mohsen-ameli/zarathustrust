import { useState, useEffect } from "react";
import { useHistory, useLocation } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import RotateLoader from 'react-spinners/RotateLoader';
import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';


let currentTime;

const SignUp = () => {
    let bot = false
    let { state }   = useLocation()
    let history     = useHistory()
    let { t }       = useTranslation()

    const [phoneExt, setPhoneExt] = useState(null)
    const [username, setUsername] = useState(null)
    const [email, setEmail] = useState(null)
    const [phoneNumber, setPhoneNumber] = useState(null)
    const [password, setPassword] = useState(null)
    const [passwordConfirm, setPasswordConfirm] = useState(null)

    const [isLoading, setIsLoading] = useState(true)

    const [errUser, setErrUser] = useState(null);
    const [errEmail, setErrEmail] = useState(null);
    const [errPN, setErrPN] = useState(null);
    const [errPass1, setErrPass1] = useState(null);
    const [errPass2, setErrPass2] = useState(null);


    useEffect(() => {
        currentTime = Date.now()

        if (!state?.fromApp) {
            history.push("/country-picker")
        }

        getPhoneExt()

        setIsLoading(false)
    }, [])


    let getPhoneExt = async () => {
        let response = await fetch(`/api/json/country_phone_codes`)

        if (response.ok) {
            let data = await response.json()
            setPhoneExt(data[state?.iso])
        }
    }


    let submit = async (e) => {
        e.preventDefault()

        // checking for bots
        if (bot || Date.now() - currentTime < 1000) {
            window.location.replace("https://youtu.be/dQw4w9WgXcQ")
        }

        setIsLoading(true)
        setErrUser(null)
        setErrEmail(null)
        setErrPN(null)
        setErrPass1(null)
        setErrPass2(null)

        if (username.length < 5) {
            setErrUser("Username has to be at least 5 characters long")
            setIsLoading(false)
        } else if (password !== passwordConfirm) {
            setErrPass2("The two passwords have to match")
            setIsLoading(false)
        } else {

            let res = await fetch("/api/signup/", {
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body: JSON.stringify({
                    "country": state?.country,
                    "ext": phoneExt,
                    "username": username,
                    "email": email,
                    "phone_number": phoneNumber,
                    "password1": password,
                    "password2": passwordConfirm
                })
            })
    
            let data = JSON.parse(await res.json())

            data.username && setErrUser(data.username[0].message)
            data.email && setErrEmail(data.email[0].message)
            data.phone_number && setErrPN(data.phone_number[0].message)
            data.password1 && setErrPass1(data.password1[0].message)
            data.password2 && setErrPass2(data.password2[0].message)

            if (Object.keys(data).length === 0) {
                history.push("/verify-email", {"data": data, "msg": t("email_verify")})
            }
            console.log(data)

            setIsLoading(false)
        }
    }

    return (
        <GoogleReCaptchaProvider reCaptchaKey={process.env.REACT_APP_RECAPTCHA_KEY} SameSite="None">
            <div className="sign-up">
                { isLoading && 
                <div className="spinner">
                    <RotateLoader color="#f8b119" size={20} />
                </div>
                }

                <div className="card text-white zarathus-card mx-auto my-3">
                    <div className="card-body">
                        <form onSubmit={e => submit(e)} autoComplete="off">
                            <h3 className="fw-normal text-center">{t("sign_up_title")}</h3>
                            <hr className="zarathus-hr" />

                            {/* Honey Pot */}
                            <input type="text" style={{ display: "none" }} onChange={() => {bot = true}} />


                            {/* Username */}
                            <div className="form-floating">
                                <input type="text" className={errUser ? "form-control is-invalid" : "form-control"} autoFocus={true} required={true}
                                maxLength="15" autoCapitalize="none" onChange={e => setUsername(e.target.value)} />

                                <label htmlFor="id_username">{t("username")}</label>

                                <span className="invalid-feedback"><strong>
                                    {errUser && errUser}
                                </strong></span>

                                <p className="form-text text-white">
                                    {t("username_help")}
                                </p>
                            </div>

                            {/* Email */}
                            <div className="form-floating"> 
                                <input type="email" className={errEmail ? "form-control is-invalid" : "form-control"} id="id_email" required={true}
                                placeholder=" " onChange={e => setEmail(e.target.value)} />

                                <label htmlFor="id_email">{t("email")}</label>

                                <span className="invalid-feedback"><strong>
                                    {errEmail && errEmail}
                                </strong></span>
                                
                                <p className="form-text text-white">
                                    {t("email_help")}
                                </p>
                            </div>


                            {/* Phone Number */}
                            <div className="d-flex">
                                <div className="input-group-text" id="phone_ext">
                                    +({phoneExt})
                                </div>
                                <div className="form-floating-group flex-grow-1">
                                    <div id="div_id_phone_number" className="form-floating mb-3">
                                        <input type="number" className={errPN ? "form-control is-invalid" : "form-control"} id="id_phone_number" required={true}
                                        placeholder=" " onChange={e => setPhoneNumber(e.target.value)} />

                                        <label htmlFor="id_phone_number">
                                            {t("phone_number")}
                                        </label>

                                        <span className="invalid-feedback"><strong>
                                            {errPN && errPN}
                                        </strong></span>
                                    </div>
                                </div>
                            </div>
                            <div className="form-text text-white" id="phone_number_help">
                                {t("phone_number_help")}
                            </div>


                            {/* Password */}
                            <div className="form-floating"> 
                                <input type="password" className={errPass1 ? "form-control is-invalid" : "form-control"} id="id_password" required={true}
                                onChange={e => setPassword(e.target.value)} />

                                <label htmlFor="id_password">{t("password")}</label>

                                <span className="invalid-feedback"><strong>
                                    {errPass1 && errPass1}
                                </strong></span>

                                <ul className="form-text text-white">
                                    {t("password_help").split("\\n").map((item, key) => (
                                        <li key={key}>{item}</li>
                                    ))}
                                </ul>
                            </div>


                            {/* Password confirm */}
                            <div className="form-floating"> 
                                <input type="password" className={errPass2 ? "form-control is-invalid" : "form-control"} id="id_password_confirm" required={true}
                                onChange={e => setPasswordConfirm(e.target.value)} />

                                <label htmlFor="id_password_confirm">{t("password_confirm")}</label>

                                <span className="invalid-feedback"><strong>
                                    {errPass2 && errPass2}
                                </strong></span>

                                <p className="form-text text-white">
                                    {t("password_confirm_help")}
                                </p>
                            </div>

                        {/* submit */}
                        <button className="neon-button-green my-2">{t("sign_up")}</button>
                    </form>


                    {/* reset pass */}
                    <div className="pt-2">
                        <small className="text-muted">
                            <a style={{color: "#f8b119c7"}} href="#">{t("reset_password")}</a>
                        </small>
                    </div>

                    </div>
                </div>
            </div>
        </GoogleReCaptchaProvider>
    );
}
 
export default SignUp;