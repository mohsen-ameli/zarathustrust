import { useState, useContext, useEffect } from "react"
import { useTranslation } from "react-i18next";
import { Link, useHistory } from "react-router-dom";

import AuthContext from "../context/AuthContext";
import RotateLoader from 'react-spinners/RotateLoader';
import useMsgSwal from "../components/useMsgSwal";


const Login = () => {
    let { loginUser, user } = useContext(AuthContext)
    const { t }       = useTranslation()
    let history = useHistory()

    const [isLoading, setIsLoading] = useState(false)
    const msgSwal                   = useMsgSwal()


    useEffect(() => {
        let id = user?.user_id

        if (id !== undefined) {
            history.push("/home")
        }

        // eslint-disable-next-line
    }, [])

    
    let submit = (e) => {
        setIsLoading(true)

        let prom = loginUser(e)
        
        prom
        .catch(err => {
            msgSwal(t(err.message), "error")
            setIsLoading(false)
        })
        
    }


    return (
        <div className="login">
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
                                    {t("username_or_email")}
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
                            <Link style={{color: "#f8b119c7"}} to="/password-reset">
                                {t("reset_password")}
                            </Link>
                        </small>
                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default Login;