import { useParams } from "react-router-dom";
import useFetch from "../components/useFetch";
import { useEffect, useState } from 'react';
import { useHistory } from "react-router-dom";

import ReactTooltip from "react-tooltip";
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner'
import axios from 'axios';
import Swal from 'sweetalert2'
import withReactContent from 'sweetalert2-react-content'


const Home = () => {
    let zero = 0
    let pk = useParams().id
    let history = useHistory()

    // const { data: currUser, isLoading, error } = useFetch("/api/currUser")
    // const { data: accData, isLoading: accLoad, error: accErr } = useFetch(`/api/accounts/${pk}`)
    // const { data: userData, isLoading: userLoad, error: userErr } = useFetch(`/api/users/${pk}`)
    // const { data: interData, isLoading: interLoad, error: interErr } = useFetch(`/api/interest/${pk}`)

    const [interest, setInterest]   = useState(zero.toFixed(20))
    const [balance, setBalance]     = useState(null)
    const [bonus, setBonus]         = useState(zero.toFixed(2))
    const [id, setId]               = useState(null)
    const [name, setName]           = useState(null)
    const [isBiz, setIsBiz]         = useState(null)
    const [currency, setCurrency]   = useState(null)

    const [isLoading, setIsLoading] = useState('Loading...');
    const [error, setError]         = useState(null);
    const [show, setShow]           = useState(false);

    let balanceStatic               = null


    // right user or not
    if (id && Number(pk) !== id) {
        history.push(`/home/${id}`)
    }


    useEffect(() => {
        const MySwal = withReactContent(Swal)

        MySwal.fire({
            title: "Confirm actions ?",
            text: `You are about to pay $`,
            icon: "warning",
            width: "20rem",
            buttonsStyling: "false",
            showClass: {
                popup: "animate__animated animate__zoomInDown",
              },
              hideClass: {
                popup: "animate__animated animate__zoomOutDown",
              },
        })
        .then(() => {
            return MySwal.fire(<p>Shorthand works too</p>)
        })

        axios.get(`/api/accounts/${pk}`)
        .then(res => {
            balanceStatic = (Number(res.data.total_balance));
            setIsLoading(false);
            setBalance(Number(res.data.total_balance));
            setBonus(Number(res.data.bonus).toFixed(2));
            interestCounter()
        })
        .catch(err => {setIsLoading(false); setError('1 An error occurred. Awkward..');; setShow(true)})

        axios.get(`/api/interest/${pk}`)
        .then(res => {
            setIsLoading(false);
            setInterest(Number(res.data.interest_rate).toFixed(20));
        })
        .catch(err => {setIsLoading(false); setError('2 An error occurred. Awkward..'); setShow(true)})

        axios.get(`/api/users/${pk}`)
        .then(res => {
            setIsLoading(false);
            setIsBiz(res.data.is_business)
            setCurrency(res.data.currency)
        })
        .catch(err => {setIsLoading(false); setError('3 An error occurred. Awkward..'); setShow(true)})

        axios.get(`/api/currUser`)
        .then(res => {
            setIsLoading(false);
            setId(res.data.id)
            setName(res.data.username)
        })
        .catch(err => {setIsLoading(false); setError('4 An error occurred. Awkward..'); setShow(true)})
    }, [])


    // interest counter
    const interestCounter = () => {
        let interest = 0
        let interestRate = 0

        let incrementCounter = () => {
            setInterest(interestRate.toFixed(20))

            /* one percent of the total balance per second */
            interest = balanceStatic * 0.01 / 31536000
            interestRate = interestRate + interest

            setTimeout(incrementCounter, 1000)
        }
        if (balanceStatic > 0) {
            incrementCounter()
        }
    }


    // cash out
    let cashOut = () => {
        fetch(`/${pk}/cash_out`)
        .then(res => {
            return res.json()
        })
        .then (data => {
            if (data.success) {
                balanceStatic = (Number(data.balance).toFixed(2))
                setBalance(Number(data.balance).toFixed(2))
                setInterest(zero.toFixed(20))
                setBonus(Number(data.bonus).toFixed(2))
            } else {
                console.log(data.failed)
            }
        })
    }


    return (
    <div className="Home">

        {show && 
        <Alert className="text-center" variant="danger" onClose={() => setShow(false)} dismissible>
            { error }
        </Alert>
        }

        { isLoading && <div className="loading">Loading...</div> }
        {/* <Spinner animation="border" /> */}

        {/************* First Part ***********/}
        <div className="d-sm-flex">
            <div className="py-2">
                <h3 className="text-capitalize">Welcome, { name } !</h3>
            </div>
            <div className="py-2 ms-auto">
                <div className="d-flex">
                    <h3>
                        Bonus: { bonus }
                    </h3>

                    <a href="#" data-tip data-for="registerTip" className="fas fa-question-circle p-2"></a>

                    <ReactTooltip id="registerTip" place="bottom" effect="solid" backgroundColor="#f8b119" textColor="black">
                        The {bonus} bonus is a gift from us to every new user. It has no expiration date!
                        Every time you transfer the accumulated interest to your balance,
                        an equal amount will be taken out of your bonus.
                    </ReactTooltip>
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
                        <h1>Ballance</h1>
                    </div>
                    <div className="align-self-center ms-3">
                        {/* onMouseOver="mouseOver()" onMouseOut="mouseOut()" */}
                        <a className="neon-button" href="#" role="button"
                        id="dropdownMenuLink" data-bs-toggle="dropdown" aria-expanded="false">
                            Wallets <i className="fas fa-caret-down"></i>
                        </a>
                    
                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink">
                            <li><a className="dropdown-item" href="{% url 'wallets:wallet-search' pk=object.pk %}">Make a New Wallet</a></li>
                                <li><hr className="dropdown-divider"></hr></li>
                                    <li>
                                        <form method="POST">
                                            <a href="?wallet-name={{ wallet.0.1 }}" name="wallet-post" value="{{ wallet.0.1 }}" className="dropdown-item">
                                                <span className="flag-icon flag-icon-{{ wallet.0.0|lower }} me-2"></span> {/*{{wallet.0.1}} ({{wallet.0.2}}) */}
                                            </a>
                                        </form>
                                    </li>
                        </ul>
                    </div>
                </div>
                {/************* card **************/}
                <div className="card text-white home-card">
                    <div className="card-body">
                        <h5 className="fw-normal">
                            { name }'s {isBiz && <>Business</>} {!isBiz && <>Personal</>} Account
                        </h5>
                        <hr className="zarathus-hr"></hr>
                        <h1 className="fw-normal">
                            { balance }
                            {/* {{ wallet_symbol }}{{ wallet_balance }} */}
                        </h1>
                            Current Balance ({currency})
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
                        <h1>Interest</h1>
                    </div>
                </div>
                {/************* bottom part (counter) **************/}
                <div className="d-flex">
                    <div className="d-flex counter-interest">
                        <div>{ interest }</div>
                    </div>
                </div>
                <br></br>
                <button onClick={() => cashOut} className="neon-button ml-2">Cash Out</button>
            </div>
        </div>


        {/************* 5 buttons **************/}
        <div className="row text-center">
            <a href="" className="col-md zoom" name="add-money">
                <i className="bi bi-download buttons-5"></i>
                <h3>Deposit</h3>
            </a>
            <a href="" className="col-md zoom" name="transfer-search">
                <i className="bi bi-send-check buttons-5"></i>
                <h3>Send Money</h3>
            </a>
            <a href="" className="col-md zoom" name="take-money">
                <i className="bi bi-upload buttons-5"></i>
                <h3>Withdraw</h3>
            </a>
            <a href="" className="col-md zoom" name="currency-exchange">
                <i className="bi bi-currency-exchange buttons-5"></i>
                <h3>Currency Exchange</h3>
            </a>
            <a href="" className="col-md zoom" name="history">
                <i className="bi bi-book-half buttons-5"></i>
                <h3>Transaction History</h3>
            </a>
        </div>

    </div>
    );
}
 
export default Home;
