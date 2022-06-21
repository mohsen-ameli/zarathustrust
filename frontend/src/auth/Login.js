import { useState, useContext } from "react"
import AuthContext from "../context/AuthContext";

const Login = () => {
    let { loginUser } = useContext(AuthContext)

    return (
        <div className="login">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <form onSubmit={loginUser}>
                        <div className="mb-2">
                            <h3 className="fw-normal text-center">Log In</h3>
                            <hr className="zarathus-hr" />

                            {/* Username */}
                            <div className="form-group form-floating mb-3" style={{color: "black"}}>
                                <input type="text" autoFocus={true} autoCapitalize="none" autoComplete="username" 
                                maxLength="150" className="form-control" placeholder="username" name="username" />
                                <label htmlFor="id_username" className=" requiredField">
                                    Username
                                </label>
                            </div>

                            {/* Password */}
                            <div className="form-group form-floating mb-3" style={{color: "black"}}> 
                                <input type="password" autoComplete="current-password" 
                                className="form-control" id="id_password" name="password" />
                                <label htmlFor="id_password" className="requiredField">
                                    Password
                                </label>
                            </div>
                        </div>

                        {/* submit */}
                        <button className="neon-button-green my-2">Log In</button>
                    </form>

                    {/* reset pass */}
                    <div className="pt-2">
                        <small className="text-muted">
                            <a style={{color: "#f8b119c7"}} href="#">
                                Reset Password ?
                            </a>
                        </small>
                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default Login;