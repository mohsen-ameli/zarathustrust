import { useState, useRef, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import RotateLoader from 'react-spinners/RotateLoader';

import ShowWallets from "../components/ShowWallets";
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";
import TransactionItem from "./TransactionItem";


const Transactions = () => {
    const DEFAULT_NUM_ITEMS = 10
    const DEFAULT_FIRST_PAGE = 1
    let { user }                        = useContext(AuthContext)
    let { t }                           = useTranslation()
    const pk                            = user?.user_id
    let api                             = useFetch()

    const link                          = useRef(null)
    const link2                         = useRef(null)

    const [allTrans, setAllTrans]       = useState([])
    const [username, setUsername]       = useState(null)
    const [symbol, setSymbol]           = useState(null)
    const [totalTrans, setTotalTrans]   = useState(null)

    const [iso2, setIso2]               = useState(null)
    const [currency, setCurrency]       = useState(null)
    const [numItems, setNumItems]       = useState(DEFAULT_NUM_ITEMS)
    const [pageNum, setPageNum]         = useState(DEFAULT_FIRST_PAGE)

    const [isLoading, setIsLoading]     = useState(true)
    const [error, setError]             = useState(null)

    const fetchStuff = async () => {
        let { response: res1, data: d1 } = await api("/api/currUser/")
        if (res1.status === 200) {
            setUsername(d1.username)
            setIso2(d1.iso2)
            setCurrency(d1.currency)
        } else {
            setError("default_error")
        }

        let { response: res2, data: d2 } = await api(`/api/transactions/${d1.iso2}/${d1.currency}/${pageNum}/${numItems}/`)
        if (res2.status === 200) {
            setAllTrans(d2.transactions)
            setSymbol(d2.currencySymbol)
            setTotalTrans(d2.counter)
        } else {
            setError("default_error")
        }

        setIsLoading(false)
    }

    useEffect(() => {
        fetchStuff()
        // eslint-disable-next-line
    }, [])

    let changeCurr = async (wallet) => {
        setIsLoading(true)
        
        let { response, data } = await api(`/api/transactions/${wallet[0]}/${wallet[1]}/1/${numItems}/`)
        if (response.status === 200) {
            setAllTrans(data.transactions)
            setSymbol(data.currencySymbol)
            setTotalTrans(data.counter)

            setIso2(wallet[0])
            setCurrency(wallet[1])

            // making sure this happens => (page x of y) has x < y relationship
            setPageNum(1)

            setIsLoading(false)
        } else {
            setError("default_error")
            setIsLoading(false)
        }
    }

    let changeNumItems = async (num) => {
        setIsLoading(true)
        setNumItems(num)
        
        let { response, data } = await api(`/api/transactions/${iso2}/${currency}/1/${num}/`)
        if (response.status === 200) {
            setAllTrans(data.transactions)
            setSymbol(data.currencySymbol)
            setTotalTrans(data.counter)

            setIsLoading(false)
        } else {
            setError("default_error")
            setIsLoading(false)
        }
    }

    let changePageNum = async (num) => {
        setIsLoading(true)

        // making sure page number of total amount of transactions (page x of y) has x < y relationship
        if (Math.ceil(totalTrans / numItems) < pageNum) {
            setPageNum(Math.ceil(totalTrans / numItems))
        } else {
            setPageNum(num)
        }
        
        let { response, data } = await api(`/api/transactions/${iso2}/${currency}/${num}/${numItems}/`)
        if (response.status === 200) {
            setAllTrans(data.transactions)
            setSymbol(data.currencySymbol)
            setTotalTrans(data.counter)

            setIsLoading(false)
        } else {
            setError("default_error")
            setIsLoading(false)
        }
    }

    let mouseOver = (num) => (num === 1) ? link.current.style.color = "black" : link2.current.style.color = "black"
    let mouseOut  = (num) => (num === 1) ? link.current.style.color = "#f8b119c7" : link2.current.style.color = "#f8b119c7"

    return (
        <div className="transactions">
            {error && <MsgAlert msg={t(error)} variant="danger" />}
            { isLoading && 
                <div className="spinner">
                    <RotateLoader color="#f8b119" size={20} />
                </div>
            }

            <div className="card mx-auto zarathus-card">
                <div className="card-body">
                    <div className="m-2 mx-auto">
                        {totalTrans !== 0 ? 
                            <><div className="mb-3 text-center">{t("pagniation")}</div>
                                <div className="mb-3 text-center">{t("total_transaction")} {totalTrans}</div>

                                <div className="align-self-center ms-3 text-center">
                                <button className="neon-button" onMouseOver={() => mouseOver(1)} onMouseOut={() => mouseOut(1)}
                                id="dropdownMenuLink" data-bs-toggle="dropdown" aria-expanded="false">
                                    {t("plz_num")} <i className="fas fa-caret-down" ref={link}></i>
                                </button>
                            
                                <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(1)} type="button">1</Link></li>
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(2)} type="button">2</Link></li>
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(5)} type="button">5</Link></li>
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(10)} type="button">10</Link></li>
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(20)} type="button">20</Link></li>
                                    <li><Link to="#" className="dropdown-item" onClick={() => changeNumItems(0)} type="button">ALL</Link></li>
                                </ul>
                            </div></>
                            : 
                            <>
                                <h5 className="text-center mb-3">{t("no_transaction")}</h5>
                                <div className="text-center">
                                    <Link to="/deposit" className="neon-button">{t("deposit")}</Link>
                                </div>
                            </>
                        }

                        <hr />
                        {/* selecting a wallet */}

                        <div className="text-center">
                            <ShowWallets pk={pk} home={false} changeCurr={changeCurr} />
                        </div>

                    </div>
                </div>
            </div>

            <br />

            {/* Transactions */}
            {allTrans.map((item, key) => (
                <div className="list-group mx-auto mb-4" key={key}>
                    <TransactionItem item={item} username={username} symbol={symbol} currency={currency} />
                </div>
            ))}

            {(!isLoading && totalTrans !== 0) &&<>
                {numItems !== 0 && 
                    <nav aria-label="Page navigation">
                        <ul className="pagination justify-content-center">
                            {pageNum !== 1 && 
                            <>
                                <li className="page-item"><button className="page-link" onClick={() => changePageNum(1)}>&laquo;</button></li>
                                <li className="page-item"><button className="page-link" onClick={() => { changePageNum(pageNum - 1); } }>Previous</button></li>
                            </>
                            }

                            <li className="page-item disabled">
                                <button className="page-link">
                                    Page {pageNum} of {Math.ceil(totalTrans / numItems)}
                                </button>
                            </li>

                            {pageNum < Math.ceil(totalTrans / numItems) && 
                            <>
                                <li className="page-item"><button className="page-link" onClick={() => changePageNum(pageNum + 1)}>Next</button></li>
                                <li className="page-item"><button className="page-link" onClick={() => changePageNum(Math.ceil(totalTrans / numItems))}>&raquo;</button></li>
                            </>
                            }
                        </ul>
                    </nav>
                }
                <div className="text-center">
                    <Link className="neon-button my-2" to="/home">{t("home")}</Link> 
                </div>
            </>}

            <br />
        </div>
    );
}
 
export default Transactions;