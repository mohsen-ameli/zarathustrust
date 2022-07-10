import { useCallback, useEffect, useState } from "react";
import { useParams, useHistory, useLocation, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';

import RotateLoader from 'react-spinners/RotateLoader';
import useFetch from "../components/useFetch";
import useMsgSwal from "../components/useMsgSwal";

const WalletConfirm = () => {
    const iso2                      = useParams().curr
    let history                     = useHistory()
    let api                         = useFetch()
    let { t }                       = useTranslation()
    let { state }                   = useLocation()

    const [wallets, setWallets]     = useState([])
    const [currency, setCurrency]   = useState(null)

    const [isLoading, setIsLoading] = useState(true)
    const msgSwal                   = useMsgSwal()

    const fetchStuff = useCallback(() => {
        let loadWallets = async () => {
            let { response, data } = await api("/api/wallets/")
            
            if (response.status === 200) {
                setWallets(data)
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }; loadWallets()

        let nextFetch = async () => {
            let { response, data } =  await api("/api/json/country_currencies_clean/")
            if (response.status === 200) {
                setCurrency(data[iso2])
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
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
                msgSwal(t("new_wallet_success", {"currency": currency}), "success")

                history.push("/home")
            } else {
                msgSwal(t("wallet_error"), "error")

                history.push("/wallet-search")
            }
        } else {
            msgSwal(t("default_error"), "error")
            setIsLoading(false)
        }
    }

    return (
        <div className="new-wallet-page">
            { isLoading && 
                <div className="spinner">
                    <RotateLoader color="#f8b119" size={20} />
                </div>
            }
            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("u_sure")}</h3>
                    <hr className="zarathus-hr"></hr>
                    
                    <h4>{t("upto_10_wallets")}</h4>
                        <p>{t("current_wallets")}</p>
                        <ul>
                            {wallets && wallets.map((wallet, i) => (
                            <li key={i}>
                                {wallet[1]} ({wallet[2]})
                            </li>
                            ))}
                        </ul>
                    <hr></hr>
                    <p>
                        {t("new_wallet", {"currency": currency})}
                    </p>
                    
                    <div className="d-flex mb-3 mt-4 justify-content-center">
                        <button className="neon-button-green my-2 me-4" id="Action" onClick={() => createWallet()}>{t("save_changed")}</button>
                        <Link className="neon-button my-2" to="/home">{t("back_to_home")}</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default WalletConfirm;