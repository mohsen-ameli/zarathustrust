import { useCallback, useEffect, useState } from "react";
import { useParams, useHistory, useLocation, Link } from "react-router-dom";
import Cookies from 'js-cookie';

import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import useFetch from "../components/useFetch";

const WalletConfirm = () => {
    const iso2                      = useParams().curr
    let history                     = useHistory()
    let api                         = useFetch()

    const [wallets, setWallets]     = useState([])
    const [currency, setCurrency]   = useState(null)

    const {state}                   = useLocation()

    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)


    const fetchStuff = useCallback(() => {
        let loadWallets = async () => {
            let { response, data } = await api("/api/wallets/")
            
            if (response.status === 200) {
                setWallets(data)
                setIsLoading(false)
            } else {
                setError('An error occurred. Awkward..')
                setShowErr(true)
                setIsLoading(false)
            }
        }; loadWallets()

        let nextFetch = async () => {
            let { response, data } =  await api("/api/json/country_currencies_clean/")
            if (response.status === 200) {
                setCurrency(data[iso2])
                setIsLoading(false)
            } else {
                setError('An error occurred. Awkward..')
                setShowErr(true)
                setIsLoading(false)
            }
        }; nextFetch()

        // eslint-disable-next-line
    }, [])

    
    useEffect(() => {
        if (!state?.fromApp) {
            history.push("/wallet-search")
        }

        fetchStuff()
        // eslint-disable-next-line
    }, [fetchStuff])


    let createWallet = async () => {
        let { response, data } = await api("/api/wallets-confirm/", {
            method: "POST",
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(
                {"currency" : currency, "iso2": iso2}
            )
        })
        if (response.status === 200) {
            if (data.success) {
                sessionStorage.setItem('msg', `You have successfully added ${currency} as one of your wallets !`)
                sessionStorage.setItem('success', true)

                history.push("/home")
            } else {
                sessionStorage.setItem('msg', "You already have that wallet!")
                sessionStorage.setItem('success', false)

                history.push("/wallet-search")
            }
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
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
                        <Link className="neon-button my-2" to="/home">Back to Home</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default WalletConfirm;