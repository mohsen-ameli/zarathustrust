import { useEffect, useState } from "react";
import { Link, useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useFetch from "../components/useFetch";
import useMsgSwal from "../components/useMsgSwal";
import { useRef } from "react";

const TransferSearch = () => {
    let { t }                       = useTranslation()
    let history                     = useHistory()
    let api                         = useFetch()
    let ref                         = useRef()

    const [data, setData]           = useState(null)
    const [user, setUser]           = useState(null)

    const [isLoading, setIsLoading] = useState(true);
    const msgSwal                   = useMsgSwal()

    useEffect(() => {
        let loadUser = async () => {
            setIsLoading(true)
            let { response, data } = await api("/api/currUser/")
    
            if (response.status === 200) {
                setUser(data.username)
            } else {
                msgSwal(t("default_error"), "error")
                setIsLoading(false)
            }
        }; loadUser()
        setIsLoading(false)
    }, [])

    let submit = (typed) => {
        api("/api/transferSearch/", {
            method: "POST",
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(
                {"person" : typed}
            )
        })
        .then(res => {
            setData(JSON.parse(res.data))
        })
        .catch(() => {msgSwal(t("default_error"), "error"); setIsLoading(false);})
    }

    let search = (typed) => {
        if (typed.length >= 3) {
            submit(typed)
        } else {
            setData(null)
        }
    }

    let handleKeyClick = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            next(data[0]['username'])
        }
    }

    let next = (username) => {
        if (ref.current.value.toLowerCase() === user.toLowerCase()) {
            msgSwal(t("cannot_send_to_self"), "error")
        } else {
            history.push(`/transfer-confirm/${username}`, { fromApp: true })
        }
    }

    return (
        <div className="transfer-search" onKeyDown={e => handleKeyClick(e)}>
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }

            <div className="card zarathus-card mx-auto">
                <div className="card-body">

                    <h3 className="fw-normal text-center">{t("send_money_info")}</h3>
                    <hr className="zarathus-hr"></hr>

                    <div className="dropdown form-floating">
                        <input type="text" id="search-input" className="form-control dropdown-toggle" data-bs-toggle="dropdown"
                            placeholder="Country" autoComplete="off" onChange={e => search(e.target.value)} ref={ref}></input>
                        <label htmlFor="search-input">{t("send_money_fields")}</label>

                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink" id="results-box">
                            {data ? data.map((item, i) => (
                                <li key={i}>
                                    <button className="dropdown-item" onClick={() => next(item['username'])}
                                        style={{textTransform: "capitalize"}}>
                                        {item['username']}
                                    </button>
                                </li>
                            )) : 
                                <li>
                                    <span className="dropdown-item disabled" style={{textTransform: "capitalize", color: "black"}}>
                                        <b>{t("no_accounts")}</b>
                                    </span>
                                </li>
                            }
                        </ul>

                    </div>

                </div>
            </div>
        </div>
    );
}
 
export default TransferSearch;