import { useEffect, useState, useContext } from "react";
import { useParams, useHistory, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";
import useMsgSwal from "../components/useMsgSwal";
import useSwal from "../components/useSwal";


const TransferConfirm = () => {
    const MAX_MESSAGE_LENGTH        = 100
    let { user_ }                   = useContext(AuthContext)
    let { t }                       = useTranslation()
    let pk                          = user_?.user_id      
    let user                        = useParams().user
    let history                     = useHistory()

    let { state }                   = useLocation()
    let api                         = useFetch()

    const [addMoney, good, money, curr,,symbol, addLoad, addError, ,] = useAddMoney(pk)

    const [colour, setColour]       = useState(null);
    const [counter, setCounter]     = useState(null);
    const [msg, setMsg]             = useState(null);

    const [isLoading, setIsLoading] = useState(true);
    const msgSwal                   = useMsgSwal()

    useEffect(() => {
        if (!state?.fromApp) {
            history.push("transfer-search")
        }
        setIsLoading(false)

        // eslint-disable-next-line
    }, [])

    let changeMsg = (typed) => {
        setCounter(typed.length)

        if (typed.length === 0) {
            setColour(null)
        } else if (typed.length > MAX_MESSAGE_LENGTH) { // red
            setColour("red")
        } else if (typed.length >= MAX_MESSAGE_LENGTH * 0.75) { // yellow
            setMsg(typed)
            setColour("yellow")
        } else if (typed.length < MAX_MESSAGE_LENGTH) { // green
            setMsg(typed)
            setColour("green")
        }
    }

    let submit = () => {
        if (counter <= MAX_MESSAGE_LENGTH && good) {
            setIsLoading(true)

            api("/api/transferConfirm/",{
                method: "POST",
                headers: {
                    'X-CSRFToken': Cookies.get('csrftoken'),
                },
                body: JSON.stringify(
                    {'reciever_name': user, 'purpose': msg, 'moneyToSend': money, 'currency': curr}
                )
            })
            .then(res => {
                if (!res.data['success']) {
                    msgSwal(t("default_error"), "error")
                } else {
                    msgSwal(t("transfer_success", {"symbol": symbol, "amount": money, "user": user}), "success")
                    history.push("/home")
                }

                setIsLoading(false)
            })
            .catch(() => {msgSwal(t("default_error"), "error"); setIsLoading(false);})

        }
    }

    const confirm = useSwal(
        t("transfer_msg", {"symbol": symbol, "amount": money, "username": user}),
        submit
    )

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            confirm()
        }
    }

    return (
        <div className="transfer-confirm" onKeyDown={e => handleKeyClick(e)}>
            {(addError) && <MsgAlert msg={addError} variant="danger" />}
            {(isLoading || addLoad) && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">
                        {t("send_money_to", {"user": user})}
                    </h3>
                    <hr className="zarathus-hr"></hr>

                    {/* amount to send */}
                    { addMoney }

                    {/* message */}
                    <div className="form-floating mb-3">
                        <input type="text" placeholder=" " autoComplete="off" onChange={e => changeMsg(e.target.value)}
                        className={colour==="red" ? "form-control is-invalid" : "form-control"} id="msg"></input>
                        <label htmlFor="msg">{t("message")}</label>
                    </div>
                    {colour && colour==="green" ? <div>{t("max_char", {"counter": counter, "max": MAX_MESSAGE_LENGTH})}</div> : null}
                    {colour && colour==="yellow" ? <div style={{color: "orange"}}>{t("max_char", {"counter": counter, "max": MAX_MESSAGE_LENGTH})}</div> : null}
                    {colour && colour==="red" ? <div className="input-error">{t("max_char_reached", {"over": counter - MAX_MESSAGE_LENGTH})}</div> : null}


                    {/* button */}
                    <button className="neon-button my-2" type="submit" onClick={() => confirm()}>{t("send")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default TransferConfirm;