import { Link } from 'react-router-dom';
import img from '../images/zarathustrust_new.png'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHome, faCircleInfo, faGlobe, faGear } from '@fortawesome/free-solid-svg-icons'
import { useRef, useContext } from 'react';
import AuthContext from '../context/AuthContext';

const Navbar = () => {
    let { user } = useContext(AuthContext)
    const nav    = useRef()

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

    return (
        <div className="navbar">
            <nav className="navbar fixed-top navbar-expand-lg navbar-dark bg-dark">
                <div className="container-sm">
                        <Link className="navbar-brand" to="/">
                            <img src={ img } alt='' width="60" height="26" className="d-inline-block align-text-top"></img>
                            <span style={{fontSize: "x-large"}}> Z</span>arathus<span style={{fontSize: "x-large"}}>T</span>rust
                        </Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent" ref={nav}>
                        <ul className="navbar-nav mr-auto">
                            <li className="nav-item">
                                <Link className="nav-link active" to="/">
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
                                <Link className="nav-link dropdown-toggle text-white" to="/" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <FontAwesomeIcon icon={faGlobe} /> <span
                                        className="flag-icon flag-icon-"></span>
                                </Link>
                                <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                    <input type="hidden" value="" />
                                    <li>
                                        <button className="dropdown-item" type="submit" value="">
                                            <span className="flag-icon flag-icon-"></span>
                                        </button>
                                    </li>
                                </ul> 
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link active" to="/">
                                    <FontAwesomeIcon icon={faGear} /> Settings
                                </Link>
                            </li>
                            { logged ?
                            <li className="nav-item">
                                <Link to="/logout" className="nav-link active">Log Out</Link>
                            </li>
                            :
                            <>
                            <li className="nav-item">
                                <Link className="nav-link active" to="/login">Log In</Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link active" to="/">Sign Up</Link>
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