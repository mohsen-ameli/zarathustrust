import { useEffect, useState, useContext, useCallback } from 'react';
import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';

import RotateLoader from 'react-spinners/RotateLoader'

import Tippy from "@tippyjs/react";
import 'tippy.js/dist/tippy.css';
import 'tippy.js/animations/scale.css';

import '../css/tooltip.css'
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";
import ShowWallets from "../components/ShowWallets";


const Home = () => {
    let zero = 0

    const [interest, setInterest]       = useState(zero.toFixed(20))
    const [balance, setBalance]         = useState(zero.toFixed(2))
    const [bonus, setBonus]             = useState(zero.toFixed(1))
    const [name, setName]               = useState(null)
    const [isBiz, setIsBiz]             = useState(null)
    const [currency, setCurrency]       = useState(null)
    const [symbol, setSymbol]           = useState(null)
    const [interestSymbol, setInterestSymbol]       = useState(null)

    const [isLoading, setIsLoading]     = useState(true)
    const [error, setError]             = useState(null)
    const [msg, setMsg]                 = useState("")
    
    let { user }                        = useContext(AuthContext)
    let { t }                           = useTranslation()
    let pk                              = user?.user_id
    let api                             = useFetch()

    let balanceStatic                   = null
    let interestRate                    = 0


    const fetchStuff = useCallback(() => {
        let loadAccount = async () => {
            let { response, data } = await api("/api/account/")
    
            if (response.status === 200) {
                // eslint-disable-next-line
                balanceStatic = (Number(data.total_balance));
                setBalance(Number(data.total_balance).toFixed(2));
                setBonus(Number(data.bonus).toFixed(1));
            } else {
                setError(t("default_error"))
                setIsLoading(false)
            }
        }; loadAccount()

        let loadAccountInterest = async () => {
            let { response, data } = await api("/api/account-interest/")
    
            if (response.status === 200) {
                setInterest(Number(data.interest_rate).toFixed(20));
                // eslint-disable-next-line
                interestRate = Number(data.interest_rate)
                interestCounter()
            } else {
                setError(t("default_error"))
                setIsLoading(false)
            }
        }; loadAccountInterest()

        let loadUser = async () => {
            let { response, data } = await api("/api/currUser/")
    
            if (response.status === 200) {
                setName(data.username)
                setIsBiz(data.is_business)
                setCurrency(data.currency)
                
                loadSymbol(data.currency)
            } else {
                setError(t("default_error"))
                setIsLoading(false)
            }
        }; loadUser()

        let loadSymbol = async (iso3) => {
            let { response, data } = await api(`/api/getCurrencySymbol/${iso3}/`)
            if (response.status === 200) {
                setInterestSymbol(data)
                setSymbol(data)
            } else {
                setError(t("default_error"))
                setIsLoading(false)
            }
        }

        setIsLoading(false);
    }, [])


    useEffect(() => {
        let success = (sessionStorage.getItem('success') === "true")
        let message = String(sessionStorage.getItem('msg'))

        // displaying any messages
        if (message !== "" && message !== "null") {
            if (!success) {
                setError(t(message))
            } else if (success) {
                setMsg(t(message))
            }
        }
        // cleaning the cookies
        sessionStorage.setItem('msg', "")
        sessionStorage.setItem('success', false)
        
        fetchStuff()
        // eslint-disable-next-line
    }, [fetchStuff])


    // interest counter
    const interestCounter = () => {
        let interest = 0
        let intRate = interestRate

        if (balanceStatic > 0) {
            let incrementCounter = () => {
                setInterest(intRate.toFixed(20))

                /* one percent of the total balance per second */
                interest = balanceStatic * 0.01 / 31536000
                intRate = intRate + interest

                setTimeout(incrementCounter, 1000)
            }; incrementCounter()
        }
    }


    // cash out
    const cashOut = async () => {
        setIsLoading(true)
        
        let {response, data} = await api("/api/cash-out/")
        if (response.status === 200) {
            if (data.success) {
                reloadP(data.amount, symbol);

                // setBalance(Number(res.balance).toFixed(2))
                // setInterest(zero.toFixed(20))
                // setBonus(Number(res.bonus).toFixed(2))

                // balanceStatic = (Number(res.balance).toFixed(2))
                // interestRate = 0

            } else {
                setError(t("cash_out_error"))
            }
            setIsLoading(false);
        } else {
            setIsLoading(false)
            setError(t("default_error"))
        }
    }


    // page refresh for cashout
    window.onload = () => {
        let reloading = sessionStorage.getItem("reloading");
        let amount = sessionStorage.getItem("amount");
        let symbol = sessionStorage.getItem("symbol");
        if (reloading) {
            setMsg(t("cash_out_success", {"symbol": symbol, "amount": amount}))

            sessionStorage.removeItem("reloading");
            sessionStorage.removeItem("amount");
            sessionStorage.removeItem("symbol");
        }
    }
    

    let reloadP = (amount, s) => {
        sessionStorage.setItem("reloading", "true");
        sessionStorage.setItem("amount", amount)
        sessionStorage.setItem("symbol", s)
        document.location.reload();
    }


    let changeCurr = (wallet) => {
        const [, iso3, symbol, balance] = wallet
        setBalance(Number(balance).toFixed(2))
        setCurrency(iso3)
        setSymbol(symbol)
    }


    return ( <div className="home-page">

        {error && <MsgAlert msg={error} variant="danger" />}
        {msg && <MsgAlert msg={msg} variant="success" />}
        { isLoading && 
        <div className="spinner">
            <RotateLoader color="#f8b119" size={20} />
        </div>
        }

        {/************* First Part ***********/}
        <div className="d-sm-flex">
            <div className="py-2">
                <h3 className="text-capitalize">{t("welcome", {"name":name})}</h3>
            </div>
            <div className="py-2 ms-auto">
                <div className="d-flex">
                    <h3>
                        {t("bonus", {"interestSymbol": interestSymbol, "bonus": bonus})}
                    </h3>

                    <Tippy content={
                        `${t("bonus_msg", {"interestSymbol": interestSymbol, "bonus": bonus})}`
                    } theme={'tomato'} animation={'scale'}>
                        <a href="#0" className="fas fa-question-circle p-2">{null}</a>
                    </Tippy>
                </div>
            </div>
        </div>
        

        {/************** Second Part **************/}
        <div className="d-md-flex bd-highlight mb-4">

            {/************* ballance card **************/}
            <div className="bd-highlight">
                {/************* top part **************/}
                <div className="d-flex mb-4">
                    <div className="pe-3">
                        <i className="bi-cash-stack home-icon-top"></i>
                    </div>

                    <div className="align-self-center">
                        <h1>{t("ballance")}</h1>
                    </div>

                    {/* Wallet */}
                    <ShowWallets pk={pk} home={true} changeCurr={changeCurr} />

                </div>
                {/************* card **************/}
                <div className="card text-white home-card">
                    <div className="card-body">
                        <h5 className="fw-normal text-capitalize">
                            {isBiz ? t("user_account_biz", {"name": name}) : t("user_account_not_biz", {"name": name})}
                        </h5>
                        <hr className="zarathus-hr"></hr>
                        <h1 className="fw-normal">
                            { symbol }{ balance }
                        </h1>
                            {t("balance", {"currency":currency})}
                    </div>
                </div>
            </div>

            {/************* Interest **************/}
            <div className="bd-highlight ms-auto">
                {/************* top part **************/}
                <div className="d-flex pb-2">
                    <div className="pe-3">
                        <i className="bi bi-piggy-bank home-icon-top"></i>
                    </div>
                    <div className="align-self-center">
                        <h1>{t("interest")}</h1>
                    </div>
                </div>
                {/************* bottom part (counter) **************/}
                <div className="d-flex">
                    <div className="d-flex counter-interest">
                        <div>{ interestSymbol }{ interest }</div>
                    </div>
                </div>
                <br></br>
                <button onClick={() => cashOut()} className="neon-button ml-2">{t("cash_out")}</button>
            </div>
        </div>


        {/************* 5 buttons **************/}
        <div className="row text-center">
            <Link to="/deposit" className="col-md zoom" name="add-money">
                <i className="bi bi-download buttons-5"></i>
                <h3>{t("deposit")}</h3>
            </Link>
            <Link to="/transfer-search" className="col-md zoom" name="transfer-search">
                <i className="bi bi-send-check buttons-5"></i>
                <h3>{t("send_money")}</h3>
            </Link>
            <Link to="/withdraw" className="col-md zoom" name="take-money">
                <i className="bi bi-upload buttons-5"></i>
                <h3>{t("withdraw")}</h3>
            </Link>
            <Link to="/currency-exchange" className="col-md zoom" name="currency-exchange">
                <i className="bi bi-currency-exchange buttons-5"></i>
                <h3>{t("currency_exchange")}</h3>
            </Link>
            <Link to="/transactions" className="col-md zoom" name="history">
                <i className="bi bi-book-half buttons-5"></i>
                <h3>{t("transaction_history")}</h3>
            </Link>
        </div>

    </div>);
}
 
export default Home;

        // const MySwal = withReactContent(Swal)

        // MySwal.fire({
        //     title: "Confirm actions ?",
        //     text: `You are about to pay $`,
        //     icon: "warning",
        //     width: "20rem",
        //     buttonsStyling: "false",
        //     showClass: {
        //         popup: "animate__animated animate__zoomInDown",
        //       },
        //       hideClass: {
        //         popup: "animate__animated animate__zoomOutDown",
        //       },
        // })
        // .then(() => {
        //     return MySwal.fire(<p>Shorthand works too</p>)
        // })