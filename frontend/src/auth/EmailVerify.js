import { useEffect } from "react";
import { useState } from "react";
import { useRef } from "react";
import { useTranslation } from "react-i18next";
import { useHistory } from 'react-router-dom'

const EmailVerify = () => {
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
        let res = await fetch("/api/email-verify/")
        
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
            history.push("/phone-verify")
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

    // let validate = e => {
    //     // let re = /^\d*\.?\d*$/;
    //     let entered = e.target.value || window.event.key
    //     let id = Number(e.target.id)

    //     if (isNaN(entered)) {
    //         console.log("not a number")
    //         inputs[id].value = ""
    //     } else {
    //         console.log("Number")
    //     }
    // }


    return (
        <div className="email-verify">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <form onSubmit={e => submit(e)} autoComplete="off">
                        <h3 className="fw-normal text-center">{t("verify_email_title")}</h3>
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
                            
                            <p className="form-text text-white">{t("email_verify")}</p>
                        </div>

                        <button className="neon-button-green my-2" type="submit">{t("verify")}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
 
export default EmailVerify;