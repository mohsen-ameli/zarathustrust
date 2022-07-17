import { t } from "i18next";

const IconUsp = () => {
    return (
        <div className="container px-4 pt-4 text-center" id="featured-3">
            <h2 className="pb-4 border-bottom display-3">{t("usp_title")}</h2>
            <div className="row g-4 py-4 row-cols-1 row-cols-lg-3">
                <div className="feature col">
                    <div className="feature-icon bg-primary bg-gradient">
                        <i className="bi bi-app-indicator"></i>
                    </div>
                    <h2>{t("usp_left_title")}</h2>
                    <p>{t("usp_left_body")}</p>
                </div>
                <div className="feature col">
                    <div className="feature-icon bg-primary bg-gradient">
                        <i className="bi bi-coin"></i>
                    </div>
                    <h2>{t("usp_middle_title")}</h2>
                    <p>{t("usp_middle_body")}</p>
                </div>
                <div className="feature col">
                    <div className="feature-icon bg-primary bg-gradient">
                        <i className="bi bi-bag-check"></i>
                    </div>
                    <h2>{t("usp_right_title")}</h2>
                    <p>{t("usp_right_body")}</p>
                </div>
            </div>
        </div>
    );
}
 
export default IconUsp;