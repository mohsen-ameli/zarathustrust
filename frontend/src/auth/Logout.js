import { useContext } from "react";
import { useEffect } from "react";
import { Link } from "react-router-dom";
import AuthContext from "../context/AuthContext";

const Logout = () => {
    let { logoutUser } = useContext(AuthContext)

    return (
        <div className="logout">
            <div className="card mx-auto text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">Are you sure you want to logout?</h3>
                    <hr className="zarathus-hr" />
                    <div className="d-flex justify-content-center">
                        <button onClick={logoutUser} className="neon-button-red">Log Out</button>
                        <Link to="/" className="neon-button ms-3">Back to Home</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default Logout;