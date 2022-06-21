import { Link } from "react-router-dom";
import { useEffect, useState } from 'react';
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'
import AuthContext from "../context/AuthContext";
import { useContext } from "react";
import useFetch from "../components/useFetch";


const DepositInfo = () => {
    let [username, setUsername]     = useState("")
    let { user }                    = useContext(AuthContext)
    let pk                          = user?.user_id
    let api                         = useFetch()

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [showErr, setShowErr]     = useState(false);

    useEffect(() => {
        api("/api/currUser")
        .then(res => {
            setUsername(res.data['username'])
            setIsLoading(false)
        })
        .catch(() => {setError('0 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})
    }, [])

    return (
        <div className="deposit-info-page">
            {showErr && 
                <Alert className="text-center" variant="danger" onClose={() => setShowErr(false)} dismissible>
                    { error }
                </Alert>
            }
            {isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto" style={{maxWidth: "40rem"}}>
                <div className="card-body">
                    <h3 className="fw-normal text-center">Deposit Money From Your Account</h3>
                    <hr className="zarathus-hr"></hr>
                    <h5 className="fw-normal">
                            In order to transfer money, please log into your
                            own bank account and use the following informaiton to transfer money. 
                            After that, when your transaction gets processed by us 
                            (<span style={{color: "#f8b119"}}>within 1 bussiness day</span>), it will show 
                            the new ballance on your wallet
                    </h5> <br></br>
                    <p className="text-capitalize">
                        name : mohsen ameli <br></br>
                        account number : 128739127312 <br></br>
                        purpose(optional) : {username && username}-{ pk }
                    </p>
                    <Link className="neon-button my-2" to="/">Home</Link>
                </div>
            </div>
        </div>
    );
}
 
export default DepositInfo;