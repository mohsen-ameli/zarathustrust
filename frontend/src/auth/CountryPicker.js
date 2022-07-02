import { t } from "i18next"
import { useCallback, useEffect } from "react"
import { useState } from "react"
import { Link, useHistory } from "react-router-dom"
import ReactCountryFlag from "react-country-flag"
import Alert from 'react-bootstrap/Alert';
import RotateLoader from 'react-spinners/RotateLoader';
import { useRef } from "react"
import useFetch from "../components/useFetch";


const CountryPicker = () => {
    let ref = useRef()
    let history = useHistory()
    let api = useFetch()
    const [countries, setCountries]     = useState([])
    const [choices, setChoices]         = useState(null)
    const [empty, setEmpty]             = useState(true)
    const [defCountry, setDefCountry]   = useState(null)
    const [defCountryIso, setDefCountryIso]   = useState(null)

    const [isLoading, setIsLoading] = useState(true)
    const [error, setError]         = useState(null)
    const [showErr, setShowErr]     = useState(false)


    const fetchStuff = useCallback(() => {
        // loading user if they are already signed in
        let loadUser = async () => {
            let { response } = await api("/api/currUser/")
    
            if (response.status === 200) {
                history.push("/home")
            }
        }; loadUser()

        // getting the country of the user based on their ip
        let getCountry = async () => {
            let response = await fetch("https://ipapi.co/json/")
    
            if (response.ok) {
                let data = await response.json()
                setDefCountry(data.country_name)
                setDefCountryIso(data.country_code)
            }
        }; getCountry()

        // getting all country names
        let loadJson = async () => {
            fetch("/api/json/country_names/", {
                method: "GET"
            })
            .then(res => {
                return res.json()
            })
            .then(data => {
                setCountries(data)
                setIsLoading(false)
            })
            .catch(() => {setError('An error occurred. Awkward..'); setShowErr(true); setIsLoading(false)})
        }; loadJson()
        // eslint-disable-next-line
    }, [])


    useEffect(() => {
        fetchStuff()
    }, [fetchStuff])


    let search = (typed) => {
        setEmpty(true)
        let arrCountries = Object.entries(countries);
        let ch = []

        if (typed.length > 0 && typed !== '') {
            arrCountries.map(item => {
                if (item[1].startsWith(typed.toLowerCase())) {
                    setEmpty(false)
                    ch.push([item[0], item[1]]) 
                }
                return ch
            })
        }
        setChoices(ch)
    }


    let next = (country, iso) => {
        history.push("/signup", { fromApp: true, country: country, iso: iso })
    }


    return (
        <div className="country-picker" onKeyDown={e => {e.key === "Enter" && next(choices[0][1], choices[0][0])}}>
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

            <div className="card text-white zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">Please Choose a Country</h3>
                    <hr className="zarathus-hr" />

                    <div className="dropdown form-floating">
                        <input type="text" className="form-control dropdown-toggle" data-bs-toggle="dropdown"
                            placeholder="Country" id="country-input" autoComplete="off"
                            defaultValue={defCountry} ref={ref} onClick={() => ref.current.value = ""} onChange={e => search(e.target.value)} />

                        <label htmlFor="country-input">Please choose a country</label>

                        <button type="submit" className="neon-button my-3" name="default-submit" value="canada" onClick={() => next(defCountry.toLowerCase(), defCountryIso)}>Next</button>

                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink" id="new-country-list">
                            {choices && choices.map((item, i) => (
                                <li key={i}>
                                    <button className="dropdown-item" onClick={() => next(item[1], item[0])}
                                        style={{textTransform: "capitalize"}}>
                                        <ReactCountryFlag
                                            countryCode={item[0]}
                                            svg
                                            style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                            title={item[0]}
                                        /> 
                                        {item[1]}
                                    </button>
                                </li>
                            ))}
                            {empty && 
                                <li>
                                <span className="dropdown-item disabled" style={{textTransform: "capitalize", color: "black"}}>
                                    <b>No countries were found.</b>
                                </span>
                            </li>
                            }
                        </ul>
                    </div>

                    <div className="d-flex text-white" style={{fontSize: "9.5pt"}}>
                        <div className="mt-3">Already have an account ?</div>
                        <Link className="mt-3 ms-2" to="/login" style={{color: "#f8b119"}}>{t("log_in")}</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
 
export default CountryPicker;