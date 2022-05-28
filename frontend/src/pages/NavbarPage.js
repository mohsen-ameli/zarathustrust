import { Link } from 'react-router-dom';
import img from '../images/zarathustrust_new.png'
import useFetch from "../components/useFetch";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faCircleInfo, faGlobe, faGears } from '@fortawesome/free-solid-svg-icons'

const Navbar = () => {
    let logged = false
    const { data, isLoading, error } = useFetch("/api/currUser", [])
    const id = data?.id

    if (id !== null) {
        logged = true
    }

    return (
        <div className="Navbar">
            { isLoading && <div className="loading">Loading...</div> }
            { error && <div className="error">{ error }</div> }

            <nav className="navbar fixed-top navbar-expand-lg navbar-dark bg-dark">
                <div className="container-sm">
                            <Link className="navbar-brand" to={`/home/${id}`}>
                            <img src={ img } alt='' width="60" height="26" className="d-inline-block align-text-top"></img>
                            <span style={{fontSize: "x-large"}}>Z</span>arathus<span style={{fontSize: "x-large"}}>T</span>rust
                        </Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul className="navbar-nav mr-auto">
                            <li className="nav-item">
                                <Link className="nav-link active" to="/account">
                                    <FontAwesomeIcon icon={faHome} /> Home
                                </Link>
                            </li>

                            <li className="nav-item">
                                <Link className="nav-link active" to="/about">
                                    <FontAwesomeIcon icon={faCircleInfo} /> About
                                </Link>
                            </li>
                        </ul>

                        <ul className="navbar-nav ms-auto">
                            <li className="nav-item dropdown">
                                <a className="nav-link dropdown-toggle text-white" href="/" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <FontAwesomeIcon icon={faGlobe} /> <span
                                        className="flag-icon flag-icon-{{ LANGUAGE_CODE }}"></span>
                                </a>
                                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                    <form className="form-inline" action="{% url 'set_language' %}" method="post">
                                        <input name="next" type="hidden" value="{{ redirect_to }}" />
                                            <li>
                                                <button className="dropdown-item {% if language.code == LANGUAGE_CODE %}selected{% endif %}" 
                                                    type="submit" name="language" value="{{ language.code }}">
                                                    <span className="flag-icon flag-icon-{{ language.code }}"></span>
                                                </button>
                                            </li>
                                    </form>
                                </ul> 
                            </li>
                            <li className="nav-item">
                                <a className="nav-link active" href="/">
                                    <FontAwesomeIcon icon={faGears} /> Settings
                                </a>
                            </li>
                            { logged && 
                            <li className="nav-item">
                                <a className="nav-link active">Log Out</a>
                            </li>
                            }
                                { !logged &&
                                    <><li className="nav-item"><a className="nav-link active" href="/">Log In</a></li><li className="nav-item"><a className="nav-link active" href="/">Sign Up</a></li></>
                                }
                        </ul>

                    </div>
                </div>
            </nav>
        </div>
    );
}
 
export default Navbar;