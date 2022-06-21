import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Cookies from 'js-cookie';
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader'
import { useContext } from "react";
import AuthContext from "../context/AuthContext";
import useFetch from "../components/useFetch";

const TransferSearch = () => {
    let { authToken }               = useContext(AuthContext)
    let api                         = useFetch()

    const [data, setData]           = useState(null)

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError]         = useState(null);
    const [showErr, setShowErr]     = useState(false);

    useEffect(() => {
        setIsLoading(false)
    }, [])

    let sendSearchData = (typed) => {
        api(`/api/transferSearch`, {
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
        .catch(() => {setError('14 An error occurred. Awkward..'); setShowErr(true); setIsLoading(false);})
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
            {showErr && 
                <Alert className="text-center" variant="danger" onClose={() => setShowErr(false)} dismissible>
                    { error }
                </Alert>
            }
            { isLoading && 
            <div className="spinner">
                <RotateLoader color="#f8b119" size={20} />
            </div>
            }
            <div className="card zarathus-card mx-auto">
                <div className="card-body">
                    

                    <h3 className="fw-normal text-center">Send Money to Others</h3>
                    <hr className="zarathus-hr"></hr>

                    <div className="dropdown form-floating">
                        <input type="text" id="search-input" className="form-control dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false"
                            placeholder="Country" autoComplete="off" onChange={e => search(e.target.value)}></input>
                        <label htmlFor="search-input">Username, Email or Phone Number</label>

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
                                    <a className="dropdown-item disabled" style={{textTransform: "capitalize", color: "black"}}>
                                        <b>No accounts were found.</b>
                                    </a>
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