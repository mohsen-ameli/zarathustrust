import { useState, useContext } from "react"
import { useTranslation } from "react-i18next";
import AuthContext from "../context/AuthContext";
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import { useEffect } from "react";

const Login = () => {
    let { loginUser } = useContext(AuthContext)
    const { t }       = useTranslation()

    const [isLoading, setIsLoading] = useState(false)
    // const [error, setError]         = useState(() => localStorage.getItem("msg") ? localStorage.getItem("msg") && setShowErr(true) : null)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)
    const [showMsg, setShowMsg]     = useState(false)
    const [msg, setMsg]             = useState("")


    useEffect(() => {
        let success = (localStorage.getItem('success') === "true")
        let message = String(localStorage.getItem('msg'))

        // displaying any messages
        if (message !== "" && message !== "null") {
            if (!success) {
                setError(message)
                setShowErr(true)
            } else if (success) {
                setMsg(message)
                setShowMsg(true)
            } else {
                setShowErr(false)
                setShowMsg(false)
            }
        }
        // cleaning the cookies
        localStorage.setItem('msg', "")
        localStorage.setItem('success', false)
    }, [])

    
    let submit = (e) => {
        setIsLoading(true)

        let prom = loginUser(e)
        
        prom
        .catch(err => {
            setError(err)
            setShowErr(true)
            setIsLoading(false)
        })
        
    }


    return (
        <div className="login">
            {showErr && 
            <Alert className="text-center" variant="danger" onClose={() => setShowErr(false)} dismissible>
                { error }
            </Alert>
            }
            {showMsg &&
            <Alert className="text-center" variant="success" onClose={() => setShowMsg(false)} dismissible>
                { msg }
            </Alert>
            }
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <form onSubmit={e => submit(e)}>
                        <div className="mb-2">
                            <h3 className="fw-normal text-center">{t("log_in")}</h3>
                            <hr className="zarathus-hr" />

                            {/* Username */}
                            <div className="form-group form-floating mb-3" style={{color: "black"}}>
                                <input type="text" autoFocus={true} autoCapitalize="none" autoComplete="username" 
                                maxLength="150" className="form-control" placeholder="username" name="username" />
                                <label htmlFor="id_username" className=" requiredField">
                                    {t("username")}
                                </label>
                            </div>

                            {/* Password */}
                            <div className="form-group form-floating mb-3" style={{color: "black"}}> 
                                <input type="password" autoComplete="current-password" 
                                className="form-control" id="id_password" name="password" />
                                <label htmlFor="id_password" className="requiredField">
                                    {t("password")}
                                </label>
                            </div>
                        </div>

                        {/* submit */}
                        <button className="neon-button-green my-2">{t("log_in")}</button>
                    </form>

                    {/* reset pass */}
                    <div className="pt-2">
                        <small className="text-muted">
                            <a style={{color: "#f8b119c7"}} href="/password-reset">
                                {t("reset_password")}
                            </a>
                        </small>
                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default Login;