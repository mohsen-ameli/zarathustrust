import { useEffect, useState, useContext } from "react";
import ReactCountryFlag from "react-country-flag";
import { useTranslation } from "react-i18next";
import useFetch from "./useFetch";


const useAddMoney = (pk) => {
    const [iso2, setIso2]               = useState(null)
    const [curr, setCurr]               = useState(null);
    const [symbol, setSymbol]           = useState(null);
    const [currencies, setCurrencies]   = useState([]);
    const [min, setMin]                 = useState(0);
    const [err, setErr]                 = useState(null);
    const [good, setGood]               = useState(false);
    const [money, setMoney]             = useState(null);

    const [isLoading, setIsLoading]     = useState(false);
    const [error, setError]             = useState(null);
    const [showErr, setShowErr]         = useState(false);

    let api                             = useFetch()
    const { t }                         = useTranslation()


    useEffect(() => {
        loadMoneyForm()
    }, [pk])


    let loadMoneyForm = async () => {
        let { response, data } = await api("/api/money-form")
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
    }


    let changeCurr = (iso, curr, symbol, min) => {
        setIso2(iso)
        setCurr(curr)
        setSymbol(symbol)
        setMin(min)
        if (money !== null && money < min) {
            setErr(t("min_warning", {"min": min, "symbol": symbol}))
            setGood(false)
        } else {
            setGood(true)
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
                        <ReactCountryFlag
                            countryCode={iso2}
                            svg
                            style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                            title={iso2}
                        />
                        { curr && curr } ({ symbol && symbol })
                    </button>

                    {/* dropdown options */}
                    <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">

                        {currencies.map((item, i) => (
                            <li key={i}>
                                <button className="dropdown-item" 
                                onClick={e => {changeCurr(item[0], item[1], item[2], item[3]); e.preventDefault()}}>
                                    <ReactCountryFlag
                                        countryCode={`${item[0]}`}
                                        svg
                                        style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                        title={`${item[0]}`}
                                    />
                                    {item[1]} ({item[2]})
                                </button>
                            </li>
                        ))}

                    </ul>
                </div>

                {/* Input */}
                <div className="form-floating flex-grow-1">
                    <input type="text" placeholder=" " className={err ? "form-control is-invalid" : "form-control"} 
                        onChange={e => changeMoney(e.target.value)} autoComplete="off"></input>
                    <label htmlFor="id_add_money">
                        {t("enter_amount")}
                    </label>
                </div>

            </div>
            <div className="input-error mt-3">{err && err}</div>
        </div>
    ), good, money, curr, iso2, symbol, isLoading, error, showErr, currencies];
}
 
export default useAddMoney;