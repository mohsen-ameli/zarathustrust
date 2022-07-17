import { t } from "i18next";

const Socials = () => {
    return (
        <div className="container text-center pb-5">
            <h1 className="display-3">{t("follow_socials")}</h1>
            <hr className="w-75" style={{display: "inline-flex"}} />
            <div className="row">
                <div className="col-4">
                    <a href="#0"><i className="bi bi-instagram social-icons"></i></a>
                </div>
                <div className="col-4">
                    <a href="#0"><i className="bi bi-twitter social-icons"></i></a>
                </div>
                <div className="col-4">
                    <a href="#0"><i className="bi bi-youtube social-icons"></i></a>
                </div>
            </div>
        </div>
    );
}
 
export default Socials;