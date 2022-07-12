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
import ShowWallets from "../components/ShowWallets";
import useMsgSwal from "../components/useMsgSwal";
import useInterest from './useInterest';

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
    const msgSwal                       = useMsgSwal()

    let { user }                        = useContext(AuthContext)
    let { t }                           = useTranslation()
    let pk                              = user?.user_id
    let api                             = useFetch()

    const interestCounter = useInterest(interest, balance, setInterest)

    const fetchStuff = useCallback(() => {
        let loadAccount = async () => {
            setIsLoading(true)
            let { response, data } = await api("/api/account/")
    
            if (response.status === 200) {
                setBalance(Number(data.total_balance).toFixed(2))
                setBonus(Number(data.bonus).toFixed(1))
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }; loadAccount()

        let loadAccountInterest = async () => {
            setIsLoading(true)
            let { response, data } = await api("/api/account-interest/")
    
            if (response.status === 200) {
                setInterest(Number(data.interest_rate).toFixed(20));
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }; loadAccountInterest()

        let loadUser = async () => {
            setIsLoading(true)
            let { response, data } = await api("/api/currUser/")
    
            if (response.status === 200) {
                setName(data.username)
                setIsBiz(data.is_business)
                setCurrency(data.currency)
                
                loadSymbol(data.currency)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }; loadUser()

        let loadSymbol = async (iso3) => {
            setIsLoading(true)
            let { response, data } = await api(`/api/getCurrencySymbol/${iso3}/`)
            
            if (response.status === 200) {
                setInterestSymbol(data)
                setSymbol(data)
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }

        // eslint-disable-next-line
    }, [])

    useEffect(() => {
        let reloading = localStorage.getItem("reloading");
        let amount = localStorage.getItem("amount");
        let symbol_ = localStorage.getItem("symbol");
        if (reloading) {
            msgSwal(t("cash_out_success", {"symbol": symbol_, "amount": amount}), "success")

            localStorage.removeItem("reloading");
            localStorage.removeItem("amount");
            localStorage.removeItem("symbol");
        }

        fetchStuff()
        // eslint-disable-next-line
    }, [fetchStuff])

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
                msgSwal(t("cash_out_error"), "error")
            }
            setIsLoading(false);
        } else {
            setIsLoading(false)
            msgSwal(t("default_error"), "error")
        }
    }

    let reloadP = (amount, symbol_) => {
        localStorage.setItem("reloading", true);
        localStorage.setItem("amount", amount);
        localStorage.setItem("symbol", symbol_);

        document.location.reload();
    }

    let changeCurr = (wallet) => {
        const [, iso3, symbol, balance] = wallet
        setBalance(Number(balance).toFixed(2))
        setCurrency(iso3)
        setSymbol(symbol)
    }

    return ( <div className="home-page">
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
                    } theme={'tomato'} animation={'scale'} placement={'bottom'}>
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
                            {t("balance", {"currency": currency})}
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
                        {/* <div>{ interestSymbol }{ interest }</div> */}
                        { interestSymbol }{interestCounter}
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