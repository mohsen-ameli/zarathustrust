import { t } from "i18next";
import { Link } from "react-router-dom";

const JoinUs = () => {
    return (
        <div className="container my-5 text-center">
            <h1 className="display-3">{t("join_us")}</h1>
            <hr />
            {/**************** 2 buttons *****************/}
            <div className="row text-center">
                <Link to="/signup" className="zoom-login">
                    <i className="fas fa-user-plus buttons-2 p-2"></i>
                    <h1 style={{fontSize: "2rem"}}>{t("sign_up")}</h1>
                </Link>
                <Link to="/login" className="zoom-login">
                    <i className="fas fa-sign-in-alt buttons-2 p-2"></i>
                    <h1 style={{fontSize: "2rem"}}>{t("log_in")}</h1>
                </Link>
            </div>
        </div>
    );
}
 
export default JoinUs;