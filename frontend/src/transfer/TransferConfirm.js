import { useEffect, useState } from "react";
import { useParams, useHistory } from "react-router-dom";
import Cookies from 'js-cookie';
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'
import { useLocation } from "react-router-dom";
import useAddMoney from "../components/useAddMoney"
import AuthContext from "../context/AuthContext";
import { useContext } from "react";
import useFetch from "../components/useFetch";
import { useTranslation } from "react-i18next";

const TransferConfirm = () => {
    let { user_ }                   = useContext(AuthContext)
    let { t }                       = useTranslation()
    let pk                          = user_?.user_id      
    let user                        = useParams().user
    let history                     = useHistory()
    let max                         = 10

    const { state }                 = useLocation()
    let api                         = useFetch()

    const [addMoney, good, money, curr,,, addLoad, addError, addShowErr] = useAddMoney(pk)
    

    const [colour, setColour]       = useState(null);
    const [counter, setCounter]     = useState(null);
    const [msg, setMsg]             = useState(null);

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [showErr, setShowErr]     = useState(false);


    useEffect(() => {
        if (!state?.fromApp) {
            history.push(`/${pk}/transfer-search`)
        }
        setIsLoading(false)
    }, [history, pk, state?.fromApp])

    let changeMsg = (typed) => {
        setCounter(typed.length)

        if (typed.length === 0) {
            setColour(null)
        } else if (typed.length > max) { // red
            setColour("red")
        } else if (typed.length >= max * 0.75) { // yellow
            setMsg(typed)
            setColour("yellow")
        } else if (typed.length < max) { // green
            setMsg(typed)
            setColour("green")
        }
    }

    let submit = () => {
        if (counter <= max && good) {
            setIsLoading(true)

            api("/api/transferConfirm",{
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
                    setError(res.data['message'])
                    setShowErr(true)
                } else {
                    sessionStorage.setItem('msg', res.data['message'])
                    sessionStorage.setItem('success', res.data['success'])
                    
                    history.push("/home")
                }

                setIsLoading(false)
            })
            .catch(() => {setError('015 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})

        }
    }

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            submit()
        }
    }

    return (
        <div className="transfer-confirm" onKeyDown={e => handleKeyClick(e)}>
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
                    {colour && colour==="green" ? <div>{t("max_char", {"counter": counter, "max": max})}</div> : null}
                    {colour && colour==="yellow" ? <div style={{color: "orange"}}>{t("max_char", {"counter": counter, "max": max})}</div> : null}
                    {colour && colour==="red" ? <div className="input-error">{t("max_char_reached")}</div> : null}


                    {/* button */}
                    <button className="neon-button my-2" type="submit" onClick={() => submit()}>{t("send")}</button>
                </div>
            </div>
        </div>
    );
}
 
export default TransferConfirm;