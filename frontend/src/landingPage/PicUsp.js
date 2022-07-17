import { t } from "i18next";

const PicUsp = () => {
    return (
        <div className="container">
            <hr className="featurette-divider" />

            <div className="row featurette py-3">
                <div className="col-md-7">
                    <h2 className="featurette-heading">{t("featureset_first_title")}</h2>
                    <p className="lead">{t("featureset_first_body")}</p>
                </div>
                <div className="col-md-5">
                    <svg className="bd-placeholder-img bd-placeholder-img-lg featurette-image img-fluid mx-auto" width="500" height="500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 500x500" preserveAspectRatio="xMidYMid slice" focusable="false"><title>Placeholder</title><rect width="100%" height="100%" fill="#eee"/><text x="50%" y="50%" fill="#aaa" dy=".3em">500x500</text></svg>
                </div>
            </div>

            <hr className="featurette-divider" />

            <div className="row featurette py-3">
                <div className="col-md-7 order-md-2">
                    <h2 className="featurette-heading">{t("featureset_second_title")}</h2>
                    <p className="lead">{t("featureset_second_body")}</p>
                </div>
                <div className="col-md-5 order-md-1">
                    <svg className="bd-placeholder-img bd-placeholder-img-lg featurette-image img-fluid mx-auto" width="500" height="500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 500x500" preserveAspectRatio="xMidYMid slice" focusable="false"><title>Placeholder</title><rect width="100%" height="100%" fill="#eee"/><text x="50%" y="50%" fill="#aaa" dy=".3em">500x500</text></svg>
                </div>
            </div>
        </div>
    );
}
 
export default PicUsp;