import { useHistory } from "react-router-dom";
import { useEffect, useState, useContext } from "react";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";
import useSwal from "../components/useSwal";
import useMsgSwal from "../components/useMsgSwal";

const Withdraw = () => {
    let { user }                    = useContext(AuthContext)
    let { t }                       = useTranslation()
    const pk                        = user?.user_id
    let api                         = useFetch()

    let history = useHistory()

    const [isLoading, setIsLoading] = useState(true);
    const msgSwal                   = useMsgSwal()

    const [addMoney, good, money, curr, ,symbol ,addLoad, addError, ,] = useAddMoney(pk)

    useEffect(() => {
        setIsLoading(false)
    }, [])

    let submit = async () => {
        if (good) {
            setIsLoading(true)

            let { response, data } = await api("/api/withdraw/",{
                method: "POST",
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken'),
                    'Content-Type':'application/json',
                },
                body: JSON.stringify(
                    {'money': money, 'currency': curr}
                )
            })

            if (response.status === 200) {
                if (!data['success']) {
                    msgSwal(t("withdraw_error"), "error")
                } else {
                    msgSwal(t("withdraw_success", {"amount": money, "currency": symbol}), "success")
                    history.push("/home")
                }
    
                setIsLoading(false)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }
    }

    const confirm = useSwal(
        t("withdraw_msg", {"symbol": symbol, "amount": money}),
        submit
    )

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            confirm()
        }
    }

    return (
        <div className="withdraw" onKeyDown={e => handleKeyClick(e)}>
            {(addError) &&  <MsgAlert msg={addError} variant="danger" />}
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

                    <button className="neon-button my-2" type="submit" onClick={() => confirm()}>{t("withdraw")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default Withdraw;