import { useEffect, useState, useContext } from "react";
import { useHistory } from "react-router-dom";
import Cookies from 'js-cookie';
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'
import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import { useTranslation } from "react-i18next";

const Deposit = () => {
    let { user }  = useContext(AuthContext)
    let pk        = user?.user_id
    let history   = useHistory()
    let api       = useFetch()
    const { t }   = useTranslation()

    const [addMoney, good, money, , , symbol, addLoad, addError, addShowErr] = useAddMoney(pk)

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [showErr, setShowErr]     = useState(false);

    useEffect(() => {
        setIsLoading(false)
    }, [])

    let submit = async () => {
        if (good) {
            setIsLoading(true)
            
            let { response } = await api("/api/deposit", {
                method: "POST",
                headers: Cookies.get('csrftoken'),
                body: JSON.stringify({"symbol" : symbol, "amount" : money})
            })
            if (response.status === 200) {
                history.push("/deposit-info")
            } else {
                setError('0 An error occurred. Awkward..')
                setShowErr(true)
                setIsLoading(false)
            }
        }
    }

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            submit()
        }
    }

    return (
        <div className="deposit-page" onKeyPress={e => {handleKeyClick(e)}}>
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


            <div className="card zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("deposit_title")}</h3>
                    <hr className="zarathus-hr"></hr>

                    {/* amount to send */}
                    {addMoney}

                    <small>{t("deposit_small_info")}</small>
                    <br></br>

                    <button className="neon-button mb-2 mt-3" type="submit" id="Action" 
                        onClick={() => submit()}>
                        {t("deposit")}
                    </button>
                </div>
            </div>
        </div>
    );
}
 
export default Deposit;