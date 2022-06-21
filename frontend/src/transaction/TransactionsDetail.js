import { useState, useEffect } from "react";
import { useHistory, useParams } from "react-router-dom";

import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import useFetch from "../components/useFetch";

const TransactionsDetail = () => {
    let tId                                     = useParams().tId
    const history                               = useHistory()
    let api                                     = useFetch()

    const [date, setDate]                       = useState(null)
    const [type, setType]                       = useState(null)
    const [price, setPrice]                     = useState(null)
    const [exPrice, setExPrice]                 = useState(null)
    const [transactor, setTransactor]           = useState(null)
    const [incoming, setIncoming]               = useState(null)
    const [currencySymbol, setCurrencySymbol]   = useState(null)
    const [message, setMessage]                 = useState(null)
    const [person, setPerson]                   = useState(null)
    // const [person2, setPerson2]                 = useState(null)
    const [wallet, setWallet]                   = useState(null)
    // const [wallet2, setWallet2]                 = useState(null)
    const [giverSymbol, setGiverSymbol]         = useState(null)
    const [recieverSymbol, setRecieverSymbol]   = useState(null)

    const [isLoading, setIsLoading]             = useState(true)
    const [error, setError]                     = useState(null)
    const [showErr, setShowErr]                 = useState(false)

    useEffect(() => {
        loadTransaction()
    }, [tId])


    let loadTransaction = async () => {
        let { response, data } = await api(`/api/transactions/${tId}`)
        if (response.status === 200) {
            let transaction = data.transaction[0]

            setType(transaction.type)
            setPrice(transaction.price?.toFixed(2))
            setExPrice(transaction.exPrice?.toFixed(2))
            setTransactor(data.transactor)
            setIncoming(data.incoming)
            setCurrencySymbol(data.currency_symbol)
            setMessage(transaction.message)

            setPerson(transaction.person)
            // setPerson2(transaction.person2)
            setWallet(transaction.wallet)
            // setWallet2(transaction.wallet2)

            setGiverSymbol(data.giverSymbol)
            setRecieverSymbol(data.recieverSymbol)

            let temp = new Date(transaction.date)

            let date_ = temp.toLocaleString('default', { month: 'long', day: 'numeric', year: 'numeric' }) 
            + " | " +  temp.toLocaleString('default', { hour: 'numeric', minute: 'numeric', second: '2-digit' })

            setDate(date_)

            setIsLoading(false)
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
        }
    }


    return (
        <div className="transactions-detail">
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
                    <h3 className="fw-normal text-center">{type} Transaction</h3>
                    <hr className="zarathus-hr"></hr>

                    <div style={{fontSize: "large"}}>
                        {type === "Transfer" ? (
                            (incoming === 1) ? 
                                <div>{currencySymbol}{price} has been transfered to you by {transactor}</div>
                            : <div>You have transfered {currencySymbol}{price} to {transactor}</div>
                        ) : ""}
                    </div>

                    <div style={{fontSize: "large"}}>
                        {type === "Deposit" ? 
                            <div>
                                Deposit to {person !== "Anonymous" && person[0]}{wallet !== "Anonymous" && wallet[0]}, for the amount {currencySymbol}{price}
                            </div>
                        : ""}
                    </div>

                    <div style={{fontSize: "large"}}>
                        {type === "Withdraw" ? 
                            <div>
                                Withdraw from {person !== "Anonymous" && person[0]}{wallet !== "Anonymous" && wallet[0]}, for the amount {currencySymbol}{price}
                            </div>
                        : ""}
                    </div>

                    <div style={{fontSize: "large"}}>
                        {type === "Cash Out" ? 
                            <div>
                                You have cashed out {currencySymbol}{price}
                            </div>
                        : ""}
                    </div>

                    <div style={{fontSize: "large"}}>
                        {type === "Exchange" ? 
                            <div>
                                You have exchanged {giverSymbol}{price} for {recieverSymbol}{exPrice}
                            </div>
                        : ""}
                    </div>

                    {message &&
                        <div style={{fontSize: "large"}}>
                            message: {message}
                        </div>
                    }

                    <br />
                    <small>{date}</small>
                    <hr />
                    <button className="neon-button" onClick={() => history.goBack()}>Back</button>
                </div>
            </div>
        </div>
    );
}
 
export default TransactionsDetail;