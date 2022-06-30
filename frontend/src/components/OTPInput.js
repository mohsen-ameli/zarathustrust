import { useEffect } from "react";
import { useState } from "react";
import { useRef } from "react";
import { useTranslation } from "react-i18next";
import { useHistory } from 'react-router-dom'

const OTPInput = ({ url, next, translationTitle, translationHelp }) => {
    let { t } = useTranslation()
    let otp = useRef()
    let [emailCode, setEmailCode] = useState(null)
    let [err, setErr] = useState(null)
    let history = useHistory()

    const inputs = otp.current?.childNodes


    useEffect(() => {
        getCode()
    }, [])


    let getCode = async () => {
        let res = await fetch(url)
        
        if (res.ok) {
            let data = await res.json()
            setEmailCode(data["code"])
        }
    }


    let submit = async (e) => {
        e.preventDefault()

        let code = ""
        for (let i = 0; i < inputs.length; i++) {
            code += String(inputs[i].value)
        }

        if (Number(code) === Number(emailCode)) {
            history.push(next)
        } else {
            setErr("You have enterd the wrong verificaiton code! Please try again.")
        }
    }


    let otpInput = e => {
        e.preventDefault()

        let allFull = false

        for (let i = 0; i < inputs.length; i++) {
            inputs[i].value && !isNaN(inputs[i].value) ? allFull = true : allFull = false
        }

        allFull ? submit(e) : setErr(null)

        let id = Number(e.target.id)

        if (e.key === "Backspace") { // backspace
            inputs[id].value = ""
            inputs[id - 1]?.focus()
        } else if (e.key === "ArrowLeft") { // left arrow go left
            inputs[id - 1]?.focus()
        } else if (e.key === "ArrowRight") { // right arrow go right
            inputs[id + 1]?.focus()
        } else if (!isNaN(e.key)) { // number
            inputs[id].value = e.key
            inputs[id + 1]?.focus()
        } else {
            inputs[id].value = ""
        }
    }


    return (
        <div className="otp-input">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <form onSubmit={e => submit(e)} autoComplete="off">
                        <h3 className="fw-normal text-center">{t(translationTitle)}</h3>
                        <hr className="zarathus-hr" />

                        <div className="form-floating"> 

                            <div className={err ? "inputs d-flex flex-row justify-content-center mt-2 is-invalid" : "inputs d-flex flex-row justify-content-center mt-2"}
                            onKeyUp={e => otpInput(e)} ref={otp} style={{caretColor: "transparent"}}>
                                <input className="m-2 text-center form-control rounded" type="text" id="0" maxLength="1" autoFocus={true} />
                                <input className="m-2 text-center form-control rounded" type="text" id="1" maxLength="1" />
                                <input className="m-2 text-center form-control rounded" type="text" id="2" maxLength="1" />
                                <input className="m-2 text-center form-control rounded" type="text" id="3" maxLength="1" />
                                <input className="m-2 text-center form-control rounded" type="text" id="4" maxLength="1" />
                                <input className="m-2 text-center form-control rounded" type="text" id="5" maxLength="1" />
                            </div>

                            <span className="invalid-feedback"><strong>
                                {err && err}
                            </strong></span>
                            
                            <p className="form-text text-white">{t(translationHelp)}</p>
                        </div>

                        <button className="neon-button-green my-2" type="submit">{t("verify")}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
 
export default OTPInput;