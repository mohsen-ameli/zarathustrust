import { useRef, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import i18next from 'i18next';
import AuthContext from '../context/AuthContext';

import img from '../images/zarathustrust_new.png'
import persia from '../images/persia.jpg'
import '../css/navbar.css'

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
    const btn = useRef()

    let logged = false
    let id = user?.user_id

    if (id !== undefined) {
        logged = true
    }

    window.addEventListener('click', (e) => {
        if (nav.current?.classList.contains("show")) { // navbar already collapsed
            if (!e.target.classList.contains("lang")) { // making sure the user is not clicking the language toggler
                btn.current.click()
            }
        }
    })

    let changeLang = (lang, code) => {
        i18next.changeLanguage(lang)
        langIcon.current?.classList.replace(langIcon.current?.classList[1],`flag-icon-${code}`)
        localStorage.setItem("code", code)
    }

    return (
        <div className="navbar">
            <nav className="navbar fixed-top navbar-expand-lg navbar-dark bg-dark">
                <div className="container-sm">
                        <Link className="navbar-brand" to={logged ? "/home" : "/"}>
                            <img src={ img } alt='' width="60" height="26" className="d-inline-block align-text-top" id="zarathus-img"></img>
                            <span style={{fontSize: "x-large"}}> Z</span>arathus<span style={{fontSize: "x-large"}}>T</span>rust
                        </Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation" ref={btn}>
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent" ref={nav}>
                        <ul className="navbar-nav mr-auto">
                            {logged &&
                            <li className="nav-item">
                                <Link className="nav-link active" to="/home">
                                <i className="fa-solid fa-house"></i> {t("home")}
                                </Link>
                            </li>
                            }

                            <li className="nav-item">
                                <Link className="nav-link active" to="/about">
                                    <i className="fa-solid fa-circle-info"></i> {t("about")}
                                </Link>
                            </li>
                        </ul>

                        <ul className="navbar-nav ms-auto">
                            <li className="nav-item dropdown">
                                <Link className="nav-link dropdown-toggle text-white lang" to="/" 
                                id="langDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i className="fa-solid fa-globe mx-1 lang"></i>
                                    {t("language")}
                                    {countryCodes[localStorage.getItem("i18nextLng")] === "ir" ? 
                                    <img alt='' height="16em" className="flag-icon mx-1 lang" src={persia} ></img> :
                                    <span className={`lang flag-icon flag-icon-${countryCodes[localStorage.getItem("i18nextLng")]} mx-1`} ref={langIcon}></span>
                                    }
                                </Link>
                                <ul className="dropdown-menu" aria-labelledby="langDropdown">
                                    <input type="hidden" value="" />
                                    <li>
                                        <Link to="#" onClick={() => changeLang("en", "en")} className="dropdown-item">
                                            <span className="flag-icon flag-icon-en mx-1"></span>
                                            English
                                        </Link>
                                        <Link to="#" onClick={() => changeLang("de", "de")} className="dropdown-item">
                                            <span className="flag-icon flag-icon-de mx-1"></span>
                                            Deutsch
                                        </Link>
                                        <Link to="#" onClick={() => changeLang("fa-IR", "ir")} className="dropdown-item">
                                            <img alt='' height="16em" className="flag-icon mx-1" src={persia} ></img>
                                            Persian
                                        </Link>
                                    </li>
                                </ul> 
                            </li>

                            { logged &&
                            <li className="nav-item">
                                <Link className="nav-link active" to="/settings">
                                    <i className="fa-solid fa-gear"></i> {t("settings")}
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
                                <Link className="nav-link active" to="/country-picker">{t("sign_up")}</Link>
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