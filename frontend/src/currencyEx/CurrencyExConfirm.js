import { useEffect, useState, useCallback } from "react";
import { useParams, useHistory, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from "js-cookie";
import RotateLoader from 'react-spinners/RotateLoader';

import useFetch from "../components/useFetch";
import useSwal from "../components/useSwal";
import useMsgSwal from "../components/useMsgSwal";

const CurrencyExConfirm = () => {
    const [fromSymbol, setFromSymbol] = useState(null)
    const [toSymbol, setToSymbol]   = useState(null)
    const [exRate, setExRate]       = useState(null)

    const [isLoading, setIsLoading] = useState(true)
    const msgSwal                   = useMsgSwal()

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
        .catch(() => {msgSwal(t("default_error"), "error"); setIsLoading(false);})

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
            if (!res.data['success']) {
                msgSwal(t("default_error"), "error")
                history.push("/currency-exchange")
            } else {
                msgSwal(t(res.data['message']), "success")
                history.push("/home")
            }
            setIsLoading(false)
        })
        .catch(() => {msgSwal(t("default_error"), "error"); setIsLoading(false);})
    }

    const confirm = useSwal(
        t("exchange_msg", {"from_symbol": fromSymbol, "from_amount": amount, "to_symbol": toSymbol, "to_amount": exRate*amount}),
        submit
    )

    return (
        <div className="currency-ex-confirm">
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

                    <button className="neon-button my-3" onClick={() => confirm()}>{t("exchange")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default CurrencyExConfirm;