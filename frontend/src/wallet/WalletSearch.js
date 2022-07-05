import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ReactCountryFlag from "react-country-flag"

import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";
import { useTranslation } from "react-i18next";

const WalletSearch = () => {
    const [currencies, setCurrencies]   = useState([])
    const [choices, setChoices]         = useState(null)
    const [empty, setEmpty]             = useState(true)

    const [isLoading, setIsLoading]     = useState(true)
    const [error, setError]             = useState(null)
    const [showMsg, setShowMsg]         = useState(false)
    const [msg, setMsg]                 = useState("")

    let api                             = useFetch()
    let { t }                           = useTranslation()


    useEffect(() => {
        let success = (sessionStorage.getItem('success') === "true")
        let m = String(sessionStorage.getItem('msg'))

        // displaying any messages
        if (m !== "" && m !== "null") {
            if (!success) {
                setError(m)
            } else if (success) {
                setMsg(m)
                setShowMsg(true)
            } else {
                setShowMsg(false)
            }
        }
        // cleaning the cookies
        sessionStorage.setItem('msg', '')
        sessionStorage.setItem('success', false)


        let loadJson = async () => {
            let { response, data } = await api("/api/json/country_currencies_clean/")
            
            if (response.status === 200) {
                setCurrencies(data)
                setIsLoading(false)
            } else {
                setError("default_error"); setIsLoading(false);
            }
        }; loadJson()

        // eslint-disable-next-line
    }, [])


    let search = (typed) => {
        setEmpty(true)
        let arrCurr = Object.entries(currencies);
        let ch = []

        if (typed.length > 0 && typed !== '') {
            arrCurr.map(item => {
                if (item[1].startsWith(typed.toUpperCase())) {
                    setEmpty(false)
                    ch.push([item[0], item[1]]) 
                }
                return ch
            })
        }
        setChoices(ch)
    }

    return (
        <div className="new-wallet-page">
            {error && <MsgAlert msg={t(error)} variant="danger" />}
            {showMsg &&
            <Alert className="text-center" variant="success" onClose={() => setShowMsg(false)} dismissible>
                { msg }
            </Alert>
            }

            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("max_wallets")}</h3>
                    <hr className="zarathus-hr"></hr>

                    <div className="dropdown form-floating">
                        <input type="text" id="country-input" className="form-control dropdown-toggle" autoComplete="off"
                        data-bs-toggle="dropdown" placeholder="Country"
                        onChange={e => search(e.target.value)}></input>
                        
                        <label htmlFor="country-input">{t("plz_choose_currency")}</label>
                        
                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink" id="new-country-list">
                            {choices && choices.map((item, i) => (
                                <li key={i}>
                                    <Link className="dropdown-item" to={{ pathname: `/wallet-search/${item[0]}`, state: { fromApp: true } }}
                                        style={{textTransform: "capitalize"}}>
                                        <ReactCountryFlag
                                            countryCode={item[0]}
                                            svg
                                            style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                            title={item[0]}
                                        /> 
                                        {item[1]}
                                    </Link>
                                </li>
                            ))}
                            {empty && 
                                <li>
                                <span className="dropdown-item disabled" style={{textTransform: "capitalize", color: "black"}}>
                                    <b>{t("no_currencies_found")}</b>
                                </span>
                            </li>
                            }
                        </ul>
                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default WalletSearch;