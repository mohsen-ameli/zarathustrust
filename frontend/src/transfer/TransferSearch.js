import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import Cookies from 'js-cookie';
import RotateLoader from 'react-spinners/RotateLoader'

import useFetch from "../components/useFetch";
import MsgAlert from "../components/MsgAlert";

const TransferSearch = () => {
    let { t }                       = useTranslation()
    let api                         = useFetch()

    const [data, setData]           = useState(null)

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);


    useEffect(() => {
        setIsLoading(false)
    }, [])


    let sendSearchData = (typed) => {
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
        .catch(() => {setError("default_error"); setIsLoading(false);})
    }


    let search = (typed) => {
        if (typed.length >= 3) {
            sendSearchData(typed)
        } else {
            setData(null)
        }
    }


    return (
        <div className="transfer-search">
            {error && <MsgAlert msg={error} variant="danger" />}
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
                            placeholder="Country" autoComplete="off" onChange={e => search(e.target.value)}></input>
                        <label htmlFor="search-input">{t("send_money_fields")}</label>

                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink" id="results-box">
                            {data ? data.map((item, i) => (
                                <li key={i}>
                                    <Link className="dropdown-item" to={{ pathname: `/${item['username']}/transfer-confirm`, state: { fromApp: true } }}
                                        style={{textTransform: "capitalize"}}>
                                        {item['username']}
                                    </Link>
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