import { t } from "i18next";
import { Link } from "react-router-dom";

const CookiePolicy = () => {
    return (
        <div className="cookie-policy">
            <div class="card text-white zarathus-card mx-auto">
                <div class="card-body">
                    <h3 class="fw-normal text-center">Cookie Policy</h3>
                    <hr class="zarathus-hr" />
                    <h5 class="fw-normal">
                        We use Google Analytics to help us grow our business. We also use cookies to help our users log in faster and to provide our customers with a better web experience. We do not have any advertisments on the website.
                    </h5>
                    <hr class="zarathus-hr" />
                    <Link class="neon-button" to="/home">{t("home")}</Link>
                </div>
            </div>
        </div>
    );
}
 
export default CookiePolicy;