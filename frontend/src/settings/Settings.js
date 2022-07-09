import { useContext } from "react";
import { useTranslation } from "react-i18next";
import { ThemeContext } from "../App";
import Switch from "react-switch";
import { Link } from "react-router-dom";

const Settings = () => {
    let { t } = useTranslation()
    let { theme, toggleTheme } = useContext(ThemeContext)

    return (
        <div className="settings">
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("settings")}</h3>
                    <hr className="zarathus-hr"></hr>

                    {/* Defaults */}
                    <h5 className="fw-normal">Defaults</h5>
                    <hr className="zarathus-hr-half" />

                    <a className="neon-button my-1" href="#0">Change Your Default Country</a>
                    <br />
                    <a className="neon-button mt-3" href="#0">Change Your Default Language</a>


                    {/* Friend Zone */}
                    <h5 className="fw-normal my-3">Friend Zone</h5>
                    <hr className="zarathus-hr-half" />

                    <Link className="neon-button" to="/invite-friend">Invite a Friend</Link>


                    {/* Changing theme */}
                    <h5 className="fw-normal my-3">Change Theme</h5>
                    <hr className="zarathus-hr-half" />

                    <Switch onChange={toggleTheme} checked={theme === "dark"} />
                    {/* <main>
                        <input className="l" type="checkbox" id="theme-btn" />
                    </main> */}


                    {/* Account */}
                    <h5 className="fw-normal my-3">Account</h5>
                    <hr className="zarathus-hr-half" />

                    <a className="neon-button mb-3" href="#0">Change Username</a><br />
                    <a className="neon-button mb-3" href="#0">Change Phone Number</a><br />
                    <Link className="neon-button mb-3" to="/password-reset">Change Password</Link><br />
                    <a className="neon-button mb-3" href="#0">Transfer To a Business Account</a><br />
                    <a className="neon-button-red mb-3" href="#0">Delete My Account</a>
                </div>
            </div>
        </div>
    );
}
 
export default Settings;