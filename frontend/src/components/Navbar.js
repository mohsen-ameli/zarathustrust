import { Link } from 'react-router-dom';
import img from '../images/zarathustrust_new.png'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faCircleInfo, faGlobe, faGear } from '@fortawesome/free-solid-svg-icons'
import { useRef, useContext } from 'react';
import AuthContext from '../context/AuthContext';
import i18next from 'i18next';
import { useTranslation } from 'react-i18next';

const Navbar = () => {
    let countryCodes = {
        "en": "en",
        "de": "de",
        "fa-IR": "ir"
    }
    let { t } = useTranslation()
    let { user } = useContext(AuthContext)
    const nav = useRef()
    const langIcon = useRef()

    let logged = false
    let id = user?.user_id

    if (id !== undefined) {
        logged = true
    }

    window.addEventListener('click', () => {
        if (nav.current?.classList.contains("show")) {
            document.querySelector("#root > div.navbar > nav > div > button").click()
        }
    })

    let changeLang = (lang, code) => {
        i18next.changeLanguage(lang)
        langIcon.current.classList.replace(langIcon.current.classList[1],`flag-icon-${code}`)
        localStorage.setItem("code", code)
    }

    return (
        <div className="navbar">
            <nav className="navbar fixed-top navbar-expand-lg navbar-dark bg-dark">
                <div className="container-sm">
                        <Link className="navbar-brand" to={logged ? "/home" : "/"}>
                            <img src={ img } alt='' width="60" height="26" className="d-inline-block align-text-top"></img>
                            <span style={{fontSize: "x-large"}}> Z</span>arathus<span style={{fontSize: "x-large"}}>T</span>rust
                        </Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent" ref={nav}>
                        <ul className="navbar-nav mr-auto">
                            {logged &&
                            <li className="nav-item">
                                <Link className="nav-link active" to="/home">
                                    <FontAwesomeIcon icon={faHome} /> {t("home")}
                                </Link>
                            </li>
                            }

                            <li className="nav-item">
                                <Link className="nav-link active" to="/about">
                                    <FontAwesomeIcon icon={faCircleInfo} /> {t("about")}
                                </Link>
                            </li>
                        </ul>

                        <ul className="navbar-nav ms-auto">
                            <li className="nav-item dropdown">
                                <Link className="nav-link dropdown-toggle text-white" to="/" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <FontAwesomeIcon icon={faGlobe} className="mx-1" />
                                    {t("language")}
                                    <span className={`flag-icon flag-icon-${countryCodes[localStorage.getItem("i18nextLng")]} mx-1`} ref={langIcon}></span>
                                </Link>
                                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                    <input type="hidden" value="" />
                                    <li>
                                        <button onClick={() => changeLang("en", "en")} className="dropdown-item">
                                            <span className="flag-icon flag-icon-en mx-1"></span>
                                            English
                                        </button>
                                        <button onClick={() => changeLang("de", "de")} className="dropdown-item">
                                            <span className="flag-icon flag-icon-de mx-1"></span>
                                            Deutsch
                                        </button>
                                        <button onClick={() => changeLang("fa-IR", "ir")} className="dropdown-item">
                                            <span className="flag-icon flag-icon-ir mx-1"></span>
                                            Persian
                                        </button>
                                    </li>
                                </ul> 
                            </li>

                            { logged &&
                            <li className="nav-item">
                                <Link className="nav-link active" to="#">
                                    <FontAwesomeIcon icon={faGear} /> {t("settings")}
                                </Link>
                            </li>
                            }
                            { logged ?
                            <li className="nav-item">
                                <Link to="/logout" className="nav-link active">{t("log_out")}</Link>
                            </li>
                            :
                            <>
                            <li className="nav-item">
                                <Link className="nav-link active" to="/login">{t("log_in")}</Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link active" to="/signup">{t("sign_up")}</Link>
                            </li>
                            </>
                            }
                        </ul>

                    </div>
                </div>
            </nav>
        </div>
    );
}
 
export default Navbar;