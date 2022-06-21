import { useEffect, useState } from "react";
import { useParams, useHistory, useLocation, Link } from "react-router-dom";
import axios from "axios";
import Cookies from 'js-cookie';

import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import { useContext } from "react";
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";

const WalletConfirm = () => {
    let { authToken, user }         = useContext(AuthContext)
    const pk                        = user?.user_id
    const iso2                      = useParams().curr
    let history                     = useHistory()
    let api                         = useFetch()

    const [wallets, setWallets]     = useState([])
    const [currency, setCurrency]   = useState(null)

    const {state}                   = useLocation()

    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)

    
    useEffect(() => {
        if (!state?.fromApp) {
            history.push(`/${pk}/wallet-search`)
        }

        loadWallets()

        nextFetch()

    }, [currency, history, pk])


    let loadWallets = async () => {
        let { response, data } = await api("/api/wallets")
        
        if (response.status === 200) {
            setWallets(data)
            setIsLoading(false)
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    let nextFetch = async () => {
        let { response, data } =  await api("/api/json/country_currencies_clean")
        if (response.status === 200) {
            setCurrency(data[iso2])
            setIsLoading(false)
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    let createWallet = async () => {
        api(`/api/wallets-confirm`, {
            method: "POST",
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(
                {"currency" : currency, "iso2": iso2}
            )
        })
        .then(() => {
            sessionStorage.setItem('msg', `You have successfully added ${currency} as one of your wallets !`)
            sessionStorage.setItem('success', true)

            history.push("/")
        })
        .catch(() => {setError('An error occurred. Awkward..'); setShowErr(true); setIsLoading(false)})
    }


    return (
        <div className="new-wallet-page">
            {showErr && 
            <Alert className="text-center" variant="danger" onClose={() => setShowErr(false)} dismissible>
                { error }
            </Alert>
            }
            { isLoading && 
                <div className="spinner">
                    <RotateLoader color="#f8b119" size={20} />
                </div>
            }
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">Are you sure ?</h3>
                    <hr className="zarathus-hr"></hr>
                    
                    <h4>You can choose up to 10 wallets with different currencies.</h4>
                        <p>Your currenct wallets are:</p>
                        <ul>
                            {wallets && wallets.map((wallet, i) => (
                            <li key={i}>
                                {wallet[1]} ({wallet[2]})
                            </li>
                            ))}
                        </ul>
                    <hr></hr>
                    <p>
                        You are about to make the currency "{ currency }" as one of your wallets.
                    </p>
                    
                    <div className="d-flex mb-3 mt-4 justify-content-center">
                        <button className="neon-button-green my-2 me-4" id="Action" onClick={() => createWallet()}>Save Changes</button>
                        <Link className="neon-button my-2" to="/">Back to Home</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default WalletConfirm;