import { Link } from "react-router-dom"; // Link component just like the anchor tag in html
import { useEffect, useState } from 'react'; // useEffect to run a function on the each render, useState for react variables 
import RotateLoader from 'react-spinners/RotateLoader' // a react-spinner called RotateLoader in order to show a loading screen when users are waiting
import AuthContext from "../context/AuthContext"; // react component which stores variables and functions that are accessible throughout the whole proj 
import { useContext } from "react"; // this is needed to use the context provided by the previous import
import useFetch from "../components/useFetch"; // custom react hook to fetch data from the backend, with authentication included
import { useTranslation } from "react-i18next";
import MsgAlert from "../components/MsgAlert";

/**
 * Component to show the deposit information required for users to be able to deposit money into their account.
 *
 * @return a bit of JSX code which shows the deposit information to the users, as well as any errors and the loading screen to the App.js
 * file and eventually to the Index.js which renders it to the DOM
 */

const DepositInfo = () => {
    /**
     * variable to set the username of the users
     * @default -> has a default value of an empty string
     */
    let [username, setUsername]     = useState("")
    /**
     * importing the react context api, which is information that is shared between all react components
     * in this case the user which is the user that is currently logged in. 
     */
    let { user }                    = useContext(AuthContext)
    /**
     * getting the primary key or the id of the currently logged in user
     */
    let pk                          = user?.user_id
    /**
     * instantiating the api variable to use the useFetch component so we can make authenticated fetch calls
     * to the backend
     */
    let api                         = useFetch()

    /**
     * variable to set the loading stage of the app
     * @default -> has a default value of true, and will be set to false once all of
     * the data is fetched successfully
     */
    const [isLoading, setIsLoading] = useState(true);
    /**
     * variable to set the error messages that might occur
     * @default -> has a default value of null since there are no errors on the 
     * first render
     */
    const [error, setError]         = useState(null);

    /**
     * Translations
     */
    const { t }   = useTranslation()

    /**
     * react hook that is a function that runs on every render
     * it runs a function "loadUser" that fetches the currUser api from the backend
     */
    useEffect(() => {
        /**
         * asynchornous function that uses the useFetch custom hook to fetch
         * the api endpoint "currUser" which will return the current user's info
         * @example -> {id: 1, username: 'NoobMoe', iso2: 'CA', currency: 'CAD'}
         */
        let loadUser = async () => {
            // awaiting the response from the backend
            let { response, data } = await api("/api/currUser/")
            // if the response was successful or not
            if (response.status === 200) {
                // setting the username
                setUsername(data['username'])

                // finished fetching so loading will be turned off
                setIsLoading(false)
            } else { // unsuccesful fetch
                // show an error message since fetching was unsuccesful
                setError("default_error")
                // set loading as false.
                setIsLoading(false)
            }
        }; loadUser()
        
        // eslint-disable-next-line
    }, [])

    /**
     * Returns a bit of JSX code which will be compiled by a Babel compiler built into react
     * to show HTML code to the user on the DOM
     */
    return (
        <div className="deposit-info-page">
            {/* showing error messages */}
            {error && <MsgAlert msg={t(error)} variant="danger" />}
            {/* loading screen */}
            {isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            {/* custom bootstrap card */}
            <div className="card text-white zarathus-card mx-auto" style={{maxWidth: "40rem"}}>
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("deposit_title")}</h3>
                    <hr className="zarathus-hr"></hr>
                    <h5 className="fw-normal">
                            {t("deposit_info")}
                    </h5> <br />
                    <p className="text-capitalize">
                        {t("deposit_card_info", {"username": username, "pk": pk}).split("\\n").map((item, i) => (
                            <span key={i}>
                            {item} <br />
                            </span>
                        ))}
                    </p>

                    {/* home button */}
                    <Link className="neon-button my-2" to="/home">{t("home")}</Link>
                </div>
            </div>
        </div>
    );
}
 
export default DepositInfo;