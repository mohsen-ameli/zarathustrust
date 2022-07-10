import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { useHistory } from 'react-router-dom'

import OtpInput from "react-otp-input";

import useMsgSwal from "./useMsgSwal";

const Otp = ({ url, next, statePrev, stateNew, translationTitle, translationHelp }) => {
    const REFRESH_TIME = 30

    let { t }   = useTranslation()
    let btn     = useRef()
    let history = useHistory()

    const [code, setCode]           = useState("");
    const [emailCode, setEmailCode] = useState(null)
    const [timer, setTimer]         = useState(REFRESH_TIME)
    const [err, setErr]             = useState(null)
    const msgSwal                   = useMsgSwal()

    useEffect(() => {
        if (!statePrev) {
            history.push("/country-picker")
        } else {
            msgSwal(t(statePrev?.msg), "info")
            getCode()
        }
        
        // eslint-disable-next-line
    }, [])

    let getCode = async () => {
        let time = REFRESH_TIME
        btn.current.style.display = "none"
        let abc = () => {
            time = time - 1
            if (time === 0) {
                btn.current.style.display = ""
                setTimer(null)
            } else {
                setTimer(time)
                setTimeout(abc, 1000)
            }
        }; abc()


        let res = await fetch(url)
        
        if (res.ok) {
            let data = await res.json()
            setEmailCode(data["code"])
        }
    }

    let submit = (code) => {
        setCode(code)
        if (code.length === 6) {
            if (Number(code) === Number(emailCode)) {
                history.push(next, stateNew)
            } else {
                setErr(t("wrong_verification"))
            }
        } else {
            setErr(null)
        }
    }

    return (
        <div className="otp">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t(translationTitle)}</h3>
                    <hr className="zarathus-hr" />

                    <div className="form-floating"> 

                        <div className="d-flex flex-row justify-content-center mt-2">
                            <OtpInput
                                shouldAutoFocus={true}
                                isInputNum={true}
                                value={code}
                                onChange={submit}
                                numInputs={6}
                                className="my-2 mx-2"
                                inputStyle={{
                                    width: "50px",
                                    height: "65px",
                                    fontSize: "x-large",
                                    border: "1px solid #ced4da",
                                    borderRadius: ".25rem",
                                    caretColor: "transparent"
                                }}
                                focusStyle={{
                                    boxShadow: "0px 0px 5px 1px var(--clr-zar)",
                                    border: "2px solid var(--clr-zar)",
                                    outline: "none",
                                }}
                            />
                        </div>

                        <span className="input-error"><strong>
                            {err && err}
                        </strong></span>
                        
                        <p className="form-text text-white">{t(translationHelp)}</p>
                    </div>

                    {timer && <small>{t("resend_verification")} {timer}</small>}
                    <button className="my-2 neon-button" ref={btn} style={{display: "none"}} onClick={() => getCode()}>{t("send_again")}</button>
                </div>
            </div>
        </div>
    );
}

export default Otp;
