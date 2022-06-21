import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useParams, useHistory, useLocation } from "react-router-dom";
import axios from "axios";
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import AuthContext from "../context/AuthContext";
import { useContext } from "react";
import useFetch from "../components/useFetch";

const CurrencyExConfirm = () => {
    let { authToken, user }         = useContext(AuthContext)
    let pk                          = user?.user_id
    let fromCurr                    = useParams().fromCurr
    let fromIso                     = useParams().fromIso
    let amount                      = useParams().amount
    let toCurr                      = useParams().toCurr
    let toIso                       = useParams().toIso

    let history                     = useHistory()
    let api                         = useFetch()

    const [fromSymbol, setFromSymbol] = useState(null)
    const [toSymbol, setToSymbol]   = useState(null)
    const [exRate, setExRate]       = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)  
    
    const { state }                 = useLocation()


    useEffect(() => {
        if (!state?.fromApp) {
            history.push(`/${pk}/currency-exchange`)
        }

        api("/api/json/currencies_symbols")
        .then(res => {
            setToSymbol(res.data[toCurr])
            setFromSymbol(res.data[fromCurr])
        })

        api(`/api/currency-exchange/${fromCurr}/${fromIso}/${amount}/${toCurr}/${toIso}`)
        .then (res => {
            setExRate(res.data['ex_rate'])
            setIsLoading(false)
        })
        .catch(() => {setError('1 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})
    }, [])

    let submit = () => {
        setIsLoading(true)
        api(`/api/currency-exchange/${fromCurr}/${fromIso}/${amount}/${toCurr}/${toIso}`, {
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
                history.push("/")
            }
            setIsLoading(false)
        })
        .catch(() => {setError('1 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})
    }


    return (
        <div className="currency-ex-confirm">
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
                    <h3 className="fw-normal text-center">Exchange Currency Confirmation</h3>
                    <hr className="zarathus-hr"></hr>
                    <h3 style={{color: "#f8b119c7"}}>We have a 0% fee for any currency exchange transaction</h3>
                    <br></br>
                    <p style={{fontSize: "large"}}>
                        You are about to exchange { fromSymbol }{ amount } to { toSymbol }{ exRate*amount }

                        <br></br>
                        
                        Exchange Rate :<br></br>
                        1{ fromCurr } = { exRate }{ toCurr }
                    </p>

                    <button className="neon-button my-3" onClick={() => submit()}>Exchange</button>
                </div>
            </div>
        </div>
    );
}
 
export default CurrencyExConfirm;