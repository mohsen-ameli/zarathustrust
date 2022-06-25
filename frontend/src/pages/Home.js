import { useEffect, useState, useRef, useContext } from 'react';
import { Link } from "react-router-dom";
import ShowWallets from "../components/ShowWallets";

import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'

import Tippy from "@tippyjs/react";
import 'tippy.js/dist/tippy.css';
import '../css/tooltip.css'
import 'tippy.js/animations/scale.css';
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import { useTranslation } from 'react-i18next';


const Home = () => {
    let zero = 0
    let { user }                        = useContext(AuthContext)
    const { t }                         = useTranslation()
    let pk                              = user?.user_id
    let api                             = useFetch()

    const [interest, setInterest]       = useState(zero.toFixed(20))
    const [balance, setBalance]         = useState(zero.toFixed(2))
    const [bonus, setBonus]             = useState(zero.toFixed(1))
    const [id, setId]                   = useState(null)
    const [name, setName]               = useState(null)
    const [isBiz, setIsBiz]             = useState(null)
    const [currency, setCurrency]       = useState(null)
    const [symbol, setSymbol]           = useState(null)
    const [interestSymbol, setInterestSymbol]       = useState(null)

    const [isLoading, setIsLoading]     = useState(true)
    const [error, setError]             = useState(null)
    const [showErr, setShowErr]         = useState(false)
    const [showMsg, setShowMsg]         = useState(false)
    const [msg, setMsg]                 = useState("")
    
    const ref                           = useRef(null)

    let balanceStatic                   = null
    let currencyStatic                  = null
    let interestRate                    = 0


    useEffect(() => {
        let success = (sessionStorage.getItem('success') === "true")
        let message = String(sessionStorage.getItem('msg'))

        // displaying any messages
        if (message !== "" && message !== "null") {
            if (!success) {
                setError(message)
                setShowErr(true)
            } else if (success) {
                setMsg(message)
                setShowMsg(true)
            } else {
                setShowErr(false)
                setShowMsg(false)
            }
        }
        // cleaning the cookies
        sessionStorage.setItem('msg', "")
        sessionStorage.setItem('success', false)
        
        // loading account
        loadAccount()

        // loading user
        loadUser()

    }, [])


    let loadAccount = async () => {
        let { response, data } = await api(`/api/account`)

        if (response.status === 200) {
            // eslint-disable-next-line
            balanceStatic = (Number(data.total_balance));
            setBalance(Number(data.total_balance).toFixed(2));
            setBonus(Number(data.bonus).toFixed(1));
            fetchInter()
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    let fetchInter = async () => {
        let { response, data } = await api(`/api/account-interest`)

        if (response.status === 200) {
            setInterest(Number(data.interest_rate).toFixed(20));
            // eslint-disable-next-line
            interestRate = Number(data.interest_rate)
            setIsLoading(false);
            interestCounter()
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    let loadUser = async () => {
        let { response, data } = await api(`/api/currUser`)

        if (response.status === 200) {
            setId(data.id)
            setName(data.username)
            setIsBiz(data.is_business)
            setCurrency(data.currency)
            // eslint-disable-next-line
            currencyStatic = data.currency
            catchh()
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    let catchh = async () => {
        let { response, data } = await api("/api/json/currencies/")

        if (response.status === 200) {
            setIsLoading(false);
            data.map(item => {
                if (item.currency.code === currencyStatic) {
                    setInterestSymbol(item.currency.symbol)
                    setSymbol(item.currency.symbol)
                }
                return null;
            })
            setIsLoading(false);
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


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
    let cashOut = () => {
        setIsLoading(true)
        
        api("/api/cash-out")
        .then (res => {
            setIsLoading(false);
            if (res.data.success) {
                reloadP(res.data.amount, symbol);

                // setBalance(Number(res.balance).toFixed(2))
                // setInterest(zero.toFixed(20))
                // setBonus(Number(res.bonus).toFixed(2))

                // balanceStatic = (Number(res.balance).toFixed(2))
                // interestRate = 0

            } else {
                setShowErr(true)
                setError(`You need at least $0.1 to be able to cash out !`)
                setIsLoading(false);
            }
        })
        .catch(() => {setIsLoading(false); setError('5 An error occurred. Awkward..'); setShowErr(true)})
    }


    // page refresh for cashout
    window.onload = () => {
        let reloading = sessionStorage.getItem("reloading");
        let amount = sessionStorage.getItem("amount");
        let s = sessionStorage.getItem("symbol");
        if (reloading) {
            setShowMsg(true)
            setMsg(`You have successfuly cashed out ${s}${amount}!`)

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


    let dismiss = (msg) => {
        const element = ref.current
        element.classList.replace("animate__fadeInDown", "animate__fadeOutDown")

        if (msg === "danger") {
            setTimeout(() => {
                setShowErr(false)
            }, 1000)
        } else {
            setTimeout(() => {
                setShowMsg(false)
            }, 1000)
        }
    }

    return ( <div className="home-page">

        {showErr && 
        <Alert className="text-center animate__animated animate__fadeInDown"
            variant="danger" onClick={() => dismiss("danger")} dismissible ref={ref}>
            { error }
        </Alert>
        }
        {showMsg &&
        <Alert className="text-center animate__animated animate__fadeInDown"
            variant="success" onClick={() => dismiss("success")} dismissible ref={ref}>
            { msg }
        </Alert>
        }
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
                        <a href="#" className="fas fa-question-circle p-2">{null}</a>
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