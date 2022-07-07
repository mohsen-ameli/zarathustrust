import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import '../css/features.css'
import '../css/fixed_bg.css'
import zarathus_5 from '../images/zarathus-5.jpg'
import zarathustrust_new from '../images/zarathustrust_new.png'
import LandingAni from './LandingAni'

const LandingPage = () => {
    let { t } = useTranslation()

    return (
    <div className="landing-page" style={{marginTop: "46px"}}>

        <LandingAni />
        
        
        {/* Starting Page Animation */}
        <div className="test-animation" id="ani"></div>

        {/* Carousel */}
        <div id="carouselExampleIndicators" className="carousel slide h-25" data-bs-ride="carousel">
            <div className="carousel-inner">
                <div className="carousel-item active" data-bs-interval="7000">
                    <img src={zarathus_5} className="d-block w-100" alt="..." />
                    <div className="carousel-caption active" style={{color: "black"}}>
                        <h1 style={{color: "black"}}>{t("carousel_title")}</h1>
                        <p>{t("carousel_body")}</p>
                    </div>
                </div>
            </div>
        </div>
        {/* Carousel */}


        {/* First USP Section */}
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
        {/* First USP Section */}


        {/* Second USP section with pics */}
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
        {/* Second USP section with pics */}


        {/* Join us now */}
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
        {/* Join us now */}


        {/* Socials */}
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
        {/* Socials */}


        {/* Footer */}
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
        {/* Footer */}

    </div>
    );
}
 
export default LandingPage;
