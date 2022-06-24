import { useTranslation } from "react-i18next";

const SignUp = () => {
    let { t } = useTranslation()

    let submit = () => {
        console.log("submiteted")
    }

    return (
        <div className="sign-up">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <form onSubmit={submit}>
                        <div className="mb-2">
                            <h3 className="fw-normal text-center">{t("sign_up")}</h3>
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

                            {/* Password confirm */}
                            <div className="form-group form-floating mb-3" style={{color: "black"}}> 
                                <input type="password" autoComplete="current-password" 
                                className="form-control" id="id_password_confirm" name="password_confirm" />
                                <label htmlFor="id_password_confirm" className="requiredField">
                                    {t("password_confirm")}
                                </label>
                            </div>
                        </div>

                        {/* submit */}
                        <button className="neon-button-green my-2">{t("log_in")}</button>
                    </form>

                    {/* reset pass */}
                    <div className="pt-2">
                        <small className="text-muted">
                            <a style={{color: "#f8b119c7"}} href="#">
                                {t("reset_password")}
                            </a>
                        </small>
                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default SignUp;