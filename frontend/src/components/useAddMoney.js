import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import ReactCountryFlag from "react-country-flag";

import useFetch from "./useFetch";
import persia from '../images/persia.jpg'
import { Link } from "react-router-dom";

const useAddMoney = () => {
    const [iso2, setIso2]               = useState(null)
    const [curr, setCurr]               = useState(null);
    const [symbol, setSymbol]           = useState(null);
    const [currencies, setCurrencies]   = useState([]);
    const [min, setMin]                 = useState(0);
    const [err, setErr]                 = useState(null);
    const [good, setGood]               = useState(false);
    const [money, setMoney]             = useState(null);

    const [isLoading, setIsLoading]     = useState(true);
    const [error, setError]             = useState(null);
    const [showErr, setShowErr]         = useState(false);

    let api                             = useFetch()
    const { t }                         = useTranslation()

    useEffect(() => {
        let loadMoneyForm = async () => {
            let { response, data } = await api("/api/money-form/")
            if (response.status === 200) {
                let options = data['currencyOptions']
    
                setIso2(options[0][0])
                setCurr(options[0][1])
                setSymbol(options[0][2])
                setMin(options[0][3])
                setCurrencies(options)
    
                setIsLoading(false)
            } else {
                setError('An error occurred. Awkward..')
                setShowErr(true)
                setIsLoading(false)
            }
        }; loadMoneyForm()

        // eslint-disable-next-line
    }, [])

    let changeCurr = (iso, curr, symbol, min) => {
        setIso2(iso)
        setCurr(curr)
        setSymbol(symbol)
        setMin(min)
        if (money !== null && money < min) {
            setErr(t("min_warning", {"min": min, "symbol": symbol}))
            setGood(false)
        } else {
            setGood(false)
            setErr(null)
        }
    }

    let changeMoney = (typed) => {
        if (typed) {
            if (isNaN(typed)) { // invalid
                setErr(t("plz_num"))
                setGood(false)
                setMoney(null)
            } else if (typed !== "") { // valid
                if (Number(typed) < min) {
                    setErr(t("min_warning", {"min": min, "symbol": symbol}))
                    setGood(false)
                } else if (typed.split(".")[1]?.length > 2) {
                    setErr(t("too_many_decimals"))
                    setGood(false)
                } else {
                    setGood(true)
                    setErr(null)
                }
                setMoney(Number(typed))
            }
        } else { // nothing (valid)
            setErr(null)
            setGood(false)
            setMoney(null)
        }
    }

    return [(
        <div className="use-add-money">
            <div className="d-flex">
                <div className="dropdown">
                    {/* dropdown button */}
                    <button style={{minHeight: "3.65rem"}} onClick={e => e.preventDefault()}
                    className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-expanded="false">
                        {iso2 === "IR" ? 
                        <img alt='' style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}} src={persia} ></img> :
                        <ReactCountryFlag
                            countryCode={iso2}
                            svg
                            style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                            title={iso2}
                        />
                        }
                        { curr && curr } ({ symbol && symbol })
                    </button>

                    {/* dropdown options */}
                    <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">

                        {currencies.map((item, i) => (
                            <li key={i}>
                                <Link to="#" className="dropdown-item" 
                                onClick={e => {changeCurr(item[0], item[1], item[2], item[3]); e.preventDefault()}}>
                                    {item[0] === "IR" ? 
                                    <img alt='' style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}} src={persia} ></img> :
                                    <ReactCountryFlag
                                        countryCode={`${item[0]}`}
                                        svg
                                        style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                        title={`${item[0]}`}
                                    />
                                    }
                                    {item[1]} ({item[2]})
                                </Link>
                            </li>
                        ))}

                    </ul>
                </div>

                {/* Input */}
                <div className="form-floating flex-grow-1">
                    <input type="text" placeholder=" " className={err ? "form-control is-invalid" : "form-control"} 
                        onChange={e => changeMoney(e.target.value)} autoComplete="off" required={true} name="money" />
                    <label htmlFor="id_add_money">
                        {t("enter_amount")}
                    </label>
                </div>

            </div>
            <div className="input-error mt-3">{err && err}</div>
        </div>
    ), good, money, curr, iso2, symbol, isLoading, error, showErr, currencies, setErr];
}
 
export default useAddMoney;