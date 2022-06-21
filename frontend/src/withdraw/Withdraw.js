import { useHistory } from "react-router-dom";
import useAddMoney from "../components/useAddMoney"
import { useEffect, useState, useContext } from "react";
import Cookies from 'js-cookie';
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";

const Withdraw = () => {
    let { user }                    = useContext(AuthContext)
    const pk                        = user?.user_id
    let api                         = useFetch()

    let history = useHistory()

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [showErr, setShowErr]     = useState(false);
    const [addMoney, good, money, curr, , ,addLoad, addError, addShowErr] = useAddMoney(pk)


    useEffect(() => {
        setIsLoading(false)
    }, [])

    let submit = () => {
        if (good) {
            setIsLoading(true)
            
            api("/api/withdraw",{
                method: "POST",
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken'),
                },
                body: JSON.stringify(
                    {'money': money, 'currency': curr}
                )
            })
            .then(res => {
                sessionStorage.setItem('msg', res.data['message'])
                sessionStorage.setItem('success', res.data['success'])
    
    
                if (!res.data['success']) {
                    setError(res.data['message'])
                    setShowErr(true)
                    sessionStorage.setItem('msg', '')
                    sessionStorage.setItem('success', false)
                } else {
                    history.push("/")
                }
    
                setIsLoading(false)
            })
            .catch(() => {setError('0 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})
        }
    }

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            submit()
        }
    }

    return (
        <div className="withdraw" onKeyDown={e => handleKeyClick(e)}>
            {(showErr || addShowErr) && 
                <Alert className="text-center" variant="danger" onClose={() => setShowErr(false)} dismissible>
                    { error || addError }
                </Alert>
            }
            {(isLoading || addLoad) && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body" style={{padding: "1.5rem"}}>
                    <h3 className="fw-normal text-center">Withdraw Money From Your Account</h3>
                    <hr className="zarathus-hr"></hr>
                    <h5 className="fw-normal">
                        In order to withdraw money, please enter the value you want to 
                        withdraw blelow <br></br> and we will transfer the amount you requested
                        to your bank account, <span style={{color: "#f8b119"}}>within 1 bussiness day.</span>
                    </h5> 
                    <br></br>

                    {/* amount to send */}
                    { addMoney }

                    <button className="neon-button my-2" type="submit" onClick={() => submit()}>Withdraw</button>
                </div>
            </div>
        </div>
    );
}
 
export default Withdraw;