import { useEffect, useState, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import useAddMoney from '../components/useAddMoney'
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import ReactCountryFlag from 'react-country-flag';
import AuthContext from '../context/AuthContext';
import { useContext } from 'react';
import useFetch from '../components/useFetch';
import { useTranslation } from 'react-i18next';

const CurrencyEx = () => {
    let { user }    = useContext(AuthContext)
    let { t }       = useTranslation()
    const pk        = user?.user_id
    const history   = useHistory()
    let api         = useFetch()
    let filtered    = null
    let first       = null

    const dflex = useRef(null)
    const arrow = useRef(null)
    const toDropMenu = useRef(null)
    
    const [addMoney, good, money, curr, iso, , , , , currencies] = useAddMoney(pk)

    if (currencies.length !== 0) {
        filtered = currencies.filter(item => {return item[0] !== curr})
        first = [filtered[0][0], filtered[0][1], filtered[0][2]]
    }

    const [iso2, setIso2]           = useState(null) 
    const [toCurr, setToCurr]       = useState(null);
    const [symbol, setSymbol]       = useState(null);

    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)

    let changeCurr = (a, b, c) => {
        setIso2(a)
        setToCurr(b)
        setSymbol(c)
    }


    useEffect(() => {
        if (window.innerWidth < 450) {
            dflex.current.classList.remove("d-flex")
            arrow.current.classList.remove("bi-arrow-right")
            arrow.current.classList.add("bi-arrow-down")
    
            dflex.current.style = "width: 100%; text-align: center;"
            arrow.current.style = "display: inline-block;"
    
            toDropMenu.current.style = "min-height: 3.65rem; width: 100%;"
        }

        if (first) {
            changeCurr(first[0], first[1], first[2])
        }

        setIsLoading(false)

        // eslint-disable-next-line
    }, [currencies])


    let submit = () => {
        if (good) {
            setIsLoading(true)

            api(`/api/currency-exchange/${curr}/${iso}/${money}/${toCurr}/${iso2}/`)
            .then (res => {
                if (!res.data['success']) {
                    setError(res.data['message'])
                    setShowErr(true)
                } else {
                    history.push(`/currency-exchange/${curr}/${iso}/${money}/${toCurr}/${iso2}`, {"fromApp": true})
                }
                setIsLoading(false)
            })
        }
    }

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            submit()
        }
    }

    return (
        <div className="currency-ex" onKeyPress={e => {handleKeyClick(e)}}>
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
                    <h3 className="fw-normal text-center">{t("exchange_title")}</h3>
                    <hr className="zarathus-hr"></hr>

                    <div className="d-flex align-items-center justify-content-center" ref={dflex}>
                        <div style={{marginTop: 14, width: "100%"}}>
                            {addMoney}
                        </div>
                        
                        <i className="bi bi-arrow-right p-2" id="arrow" ref={arrow}></i>

                        <div className="dropdown">
                            <button style={{minHeight: "3.65rem"}} className="btn btn-secondary dropdown-toggle" type="button" 
                            id="toDropdownMenu" ref={toDropMenu} data-bs-toggle="dropdown" aria-expanded="false">
                                <ReactCountryFlag
                                    countryCode={iso2}
                                    svg
                                    style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                    title={iso2}
                                />
                                {toCurr} ({symbol})
                            </button>
                            <ul className="dropdown-menu" aria-labelledby="toDropdownMenu" id="dropdown-to-item">
                                {filtered && filtered.map((item, i) => (
                                    <li key={i}>
                                        <button className="dropdown-item"
                                            onClick={() => changeCurr(item[0], item[1], item[2])}>
                                            <ReactCountryFlag
                                                countryCode={item[0]}
                                                svg
                                                style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                                title={item[0]}
                                            />
                                            {item[1]} ({item[2]})
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <button className="neon-button my-3" onClick={() => submit()}>{t("next")}</button>

                </div>
            </div>
        </div>
    );
}
 
export default CurrencyEx;