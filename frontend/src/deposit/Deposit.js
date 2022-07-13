import { useEffect, useState, useContext } from "react";
import { useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import useMsgSwal from "../components/useMsgSwal";

const Deposit = () => {
    let { user }  = useContext(AuthContext)
    let pk        = user?.user_id
    let history   = useHistory()
    let api       = useFetch()
    const { t }   = useTranslation()

    const [addMoney, good, money, , , symbol, addLoad, , err, setErr] = useAddMoney(pk)

    const [submitted, setSubmitted] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const msgSwal                   = useMsgSwal()

    console.log(err)

    useEffect(() => {
        // let fetchStuff = async () => {
        //     let { response, data } = await api("/api/get-banking-info/")

        //     if (response.status === 200) {
        //         !data.bank && history.push("/require-banking")
        //     }
        // }; fetchStuff()
        setIsLoading(false)

        // eslint-disable-next-line
    }, [])

    let submit = async (e) => {
        e.preventDefault()

        if (good) {
            if (!submitted) {
                setIsLoading(true)
                setSubmitted(true)
    
                let { response } = await api("/api/deposit/", {
                    method: "POST",
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken'),
                        'Content-Type':'application/json',
                    },
                    body: JSON.stringify({"symbol" : symbol, "amount" : money})
                })
    
                if (response.status === 200) {
                    msgSwal(t("deposit_success", {"symbol": symbol, "amount": money}), "success")
                    history.push("/deposit-info")
                } else {
                    msgSwal(t("default_error"), "error")
                    setIsLoading(false)
                }
            } else {
                msgSwal(t("default_error"), "error")
            }   
        } else if (money === null && err === null) {
            setErr(t("enter_value_error"))
        }
    }

    let handleKeyClick = e => {
        if (e.key === 'Enter') {
            submit(e)
        }
    }

    return (
        <div className="deposit-page" onKeyPress={e => handleKeyClick(e)}>
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
                        onClick={e => submit(e)}>
                        {t("deposit")}
                    </button>
                </div>
            </div>
        </div>
    );
}
 
export default Deposit;