import { useHistory } from "react-router-dom";
import { useEffect, useState, useContext } from "react";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";

const Withdraw = () => {
    let { user }                    = useContext(AuthContext)
    let { t }                       = useTranslation()
    const pk                        = user?.user_id
    let api                         = useFetch()

    let history = useHistory()

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [addMoney, good, money, curr, , ,addLoad, addError, ,] = useAddMoney(pk)


    useEffect(() => {
        setIsLoading(false)
    }, [])


    let submit = () => {
        if (good) {
            setIsLoading(true)
            
            api("/api/withdraw/",{
                method: "POST",
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken'),
                    'Content-Type':'application/json',
                },
                body: JSON.stringify(
                    {'money': money, 'currency': curr}
                )
            })
            .then(res => {    
                if (!res.data['success']) {
                    setError(t("withdraw_error"))
                } else {
                    sessionStorage.setItem('msg', t("withdraw_success", {"amount": money, "currency": res.data['userCurrencySymbol']}))
                    sessionStorage.setItem('success', true)

                    history.push("/home")
                }
    
                setIsLoading(false)
            })
            .catch(() => {setError('0 An error occurred. Awkward..'); setIsLoading(false);})
        }
    }


    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            submit()
        }
    }


    return (
        <div className="withdraw" onKeyDown={e => handleKeyClick(e)}>
            {(error || addError) &&  <MsgAlert msg={error || addError} variant="danger" />}
            {(isLoading || addLoad) && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body" style={{padding: "1.5rem"}}>
                    <h3 className="fw-normal text-center">{t("withdraw_title")}</h3>
                    <hr className="zarathus-hr"></hr>
                    <h5 className="fw-normal">
                        {t("withdraw_info")}
                    </h5> 
                    <br></br>

                    {/* amount to send */}
                    { addMoney }

                    <button className="neon-button my-2" type="submit" onClick={() => submit()}>{t("withdraw")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default Withdraw;