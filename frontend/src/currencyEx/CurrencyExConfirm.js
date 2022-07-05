import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useParams, useHistory, useLocation } from "react-router-dom";
import RotateLoader from 'react-spinners/RotateLoader';
import useFetch from "../components/useFetch";
import { useTranslation } from "react-i18next";
import { useCallback } from "react";
import MsgAlert from "../components/MsgAlert";

const CurrencyExConfirm = () => {
    const [fromSymbol, setFromSymbol] = useState(null)
    const [toSymbol, setToSymbol]   = useState(null)
    const [exRate, setExRate]       = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)

    const { state }                 = useLocation()
    let { t }                       = useTranslation()
    let fromCurr                    = useParams().fromCurr
    let fromIso                     = useParams().fromIso
    let amount                      = useParams().amount
    let toCurr                      = useParams().toCurr
    let toIso                       = useParams().toIso

    let history                     = useHistory()
    let api                         = useFetch()

    
    const fetchStuff = useCallback(() => {
        api("/api/json/currencies_symbols/")
        .then(res => {
            setToSymbol(res.data[toCurr])
            setFromSymbol(res.data[fromCurr])
        })

        api(`/api/currency-exchange/${fromCurr}/${fromIso}/${amount}/${toCurr}/${toIso}/`)
        .then (res => {
            setExRate(res.data['ex_rate'])
            setIsLoading(false)
        })
        .catch(() => {setError("default_error"); setIsLoading(false);})

        // eslint-disable-next-line
    }, [])

    useEffect(() => {
        if (!state?.fromApp) {
            history.push("/currency-exchange")
        }

        fetchStuff()
        // eslint-disable-next-line
    }, [fetchStuff])

    let submit = () => {
        setIsLoading(true)
        api(`/api/currency-exchange/${fromCurr}/${fromIso}/${amount}/${toCurr}/${toIso}/`, {
            method: "POST",
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(
                {"toCurr":toCurr,
                "toIso":toIso,
                "fromCurr":fromCurr,
                "fromIso":fromIso,
                "amount" : amount}
            )
        })
        .then (res => {
            sessionStorage.setItem('success', res.data['success'])
            sessionStorage.setItem('msg', res.data['message'])

            if (!res.data['success']) {
                history.push("/currency-exchange")
            } else {
                history.push("/home")
            }
            setIsLoading(false)
        })
        .catch(() => {setError("default_error"); setIsLoading(false);})
    }


    return (
        <div className="currency-ex-confirm">
            {error && <MsgAlert msg={t(error)} variant="danger" />}
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("exchange_confirm")}</h3>
                    <hr className="zarathus-hr"></hr>
                    <h3 style={{color: "#f8b119c7"}}>{t("exchange_confirm_info")}</h3>
                    <br></br>
                    <p style={{fontSize: "large"}}>
                        {t("exchange_info", {"fromSymbol": fromSymbol, "amount": amount, "toSymbol": toSymbol, "toRate": exRate*amount})}
                        
                        <br></br>
                        
                        {t("exchange_rate")}<br></br>
                        1{ fromCurr } = { exRate }{ toCurr }
                    </p>

                    <button className="neon-button my-3" onClick={() => submit()}>{t("exchange")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default CurrencyExConfirm;