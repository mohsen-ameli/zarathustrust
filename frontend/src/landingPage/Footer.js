import { t } from "i18next";
import { Link } from "react-router-dom";
import zarathustrust_new from '../images/zarathustrust_new.png'

const Footer = () => {
    return (
        <div id="footer">
            <div className="container">
                <footer className="d-flex flex-wrap justify-content-between align-items-center py-3 my-4">
                    <p className="col-md-4 mb-0 text-muted">© 2022 ZarathusTrust</p>
                
                    <span style={{cursor: "default"}} className="col-md-4 d-flex align-items-center justify-content-center mb-3 mb-md-0 me-md-auto link-dark text-decoration-none">
                        <img src={zarathustrust_new} className="bi me-2" width="60" height="26" alt="" />
                    </span>
                
                    <ul className="nav col-md-4 justify-content-end">
                        <li className="nav-item"><a href="#0" className="nav-link px-2 text-muted">{t("home")}</a></li>
                        <li className="nav-item"><Link to="/login" className="nav-link px-2 text-muted">{t("log_in")}</Link></li>
                        <li className="nav-item"><Link to="/country-picker" className="nav-link px-2 text-muted">{t("sign_up")}</Link></li>
                        <li className="nav-item"><a href="#0" className="nav-link px-2 text-muted">FAQs</a></li>
                        <li className="nav-item"><Link to="/about" className="nav-link px-2 text-muted">{t("about")}</Link></li>
                    </ul>

                    {/*  under dev */}
                    <div className="text-muted pt-3" id="under-dev">{t("under_dev")}</div>
                </footer>
            </div>
        </div>
    );
}
 
export default Footer;