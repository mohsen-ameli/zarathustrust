import { t } from "i18next";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {CopyToClipboard} from 'react-copy-to-clipboard';
import RotateLoader from 'react-spinners/RotateLoader'

import useFetch from "../components/useFetch";

const InviteFriend = () => {
    const [code, setCode] = useState(null)
    const [copyTxt, setCopyTxt] = useState("copy")
    const [isLoading, setIsLoading] = useState(true)
    let api = useFetch()

    useEffect(() => {
        let loadCode = async () => {
            let { response, data } = await api("/api/invite-friend/")
            if (response.status === 200) {
                setCode(data.code)
            }
            setIsLoading(false)
        }; loadCode()

        // eslint-disable-next-line
    }, [])

    let copy = () => {
        setCopyTxt("copied")
        // let textField = document.createElement('textarea')
        // textField.innerText = code
        // document.body.appendChild(textField)
        // textField.select()
        // document.execCommand('copy')
        // textField.remove()
        navigator.clipboard.writeText(code)
    }

    return (
        <div className="invite-friend">
            {isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">{t("referral_code")}</h3>
                    <hr className="zarathus-hr" />
                    <p className="card-text">{t("referral_body")}</p>

                    <div className="d-flex">
                        {code && <>
                            <h5 className="fw-bold mt-2">
                                {t("referral_code")}: {code}
                            </h5>
                            <CopyToClipboard text={code}>
                            <button className="neon-button-green mx-2" onClick={() => copy()}>{t(`${copyTxt}`)}</button>
                            </CopyToClipboard>
                        </>}
                    </div>

                    <hr className="zarathus-hr" />
                    
                    <Link className="neon-button my-2" to="/home">{t("home")}</Link>
                </div>
            </div>
        </div>
    );
}
 
export default InviteFriend;