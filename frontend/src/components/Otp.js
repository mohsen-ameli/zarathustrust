import OtpInput from "react-otp-input";
import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { useHistory } from 'react-router-dom'
import Alert from 'react-bootstrap/Alert';

const Otp = ({ url, next, statePrev, stateNew, translationTitle, translationHelp }) => {
    const REFRESH_TIME = 5

    let { t }   = useTranslation()
    let btn     = useRef()
    let history = useHistory()

    const [code, setCode]           = useState("");
    const [emailCode, setEmailCode] = useState(null)
    const [timer, setTimer]         = useState(REFRESH_TIME)
    const [err, setErr]             = useState(null)
    const [showMsg, setShowMsg]     = useState(false)
    const [msg, setMsg]             = useState(null)


    useEffect(() => {
        setMsg(statePrev?.msg)
        setShowMsg(true)
        getCode()
        
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
                setErr("You have enterd the wrong verificaiton code! Please try again.")
            }
        } else {
            setErr(null)
        }
    }


    return (
        <div className="otp">
            {showMsg &&
            <Alert className="text-center" variant="success" onClose={() => setShowMsg(false)} dismissible>
                { msg && msg }
            </Alert>
            }

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

                    {timer && <small>Resend verificaiton code in: {timer}</small>}
                    <button className="my-2 neon-button" ref={btn} style={{display: "none"}} onClick={() => getCode()}>{t("send_again")}</button>
                </div>
            </div>
        </div>
    );
}

export default Otp;
