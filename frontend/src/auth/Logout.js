import { useContext } from "react";
import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import AuthContext from "../context/AuthContext";

const Logout = () => {
    let { logoutUser } = useContext(AuthContext)
    const { t }        = useTranslation()

    return (
        <div className="logout">
            <div className="card mx-auto text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("log_out_confirm")}</h3>
                    <hr className="zarathus-hr" />
                    <div className="d-flex justify-content-center">
                        <button onClick={logoutUser} className="neon-button-red">{t("log_out")}</button>
                        <Link to="/home" className="neon-button ms-3">{t("back_to_home")}</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default Logout;