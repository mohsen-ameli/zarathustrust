import { useEffect, useRef, useState } from "react"
import { Link } from "react-router-dom"
import ReactCountryFlag from "react-country-flag"
import useFetch from "./useFetch"
import { useTranslation } from "react-i18next"

const ShowWallets = ({pk, home, changeCurr}) => {
    const [wallets, setWallets] = useState([])
    let link                    = useRef()
    let api                     = useFetch()
    const { t }                 = useTranslation()
    
    useEffect(() => {
        loadWallets()
    }, [])


    let loadWallets = async () => {
        let { response, data } = await api(`/api/wallets`)
        if (response.status === 200) {
            setWallets(data)
        }
    }

    
    let mouseOver = () => {
        link.current.style.color = "black"
    }
    let mouseOut = () => {
        link.current.style.color = "#f8b119c7"
    }


    return (
        <div className={"show-wallets dropdown align-self-center ms-3"}>
            <a className="neon-button" href="#" role="button" onMouseOver={() => mouseOver()} onMouseOut={() => mouseOut()}
            id="dropdownMenuLink" data-bs-toggle="dropdown" aria-expanded="false">
                {t("wallets")} <i className="fas fa-caret-down" ref={link}></i>
            </a>
        
            <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink">

                {home &&<>
                <li><Link className="dropdown-item" to="/wallet-search">{t("make_new_wallet")}</Link></li>
                <li><hr className="dropdown-divider"></hr></li>
                </>}

                <li>
                {wallets && wallets.map((wallet, i) => (
                    <span key={i}>
                        <button name="wallet-post" onClick={() => changeCurr(wallet)}
                            value={wallet[0]} className="dropdown-item">
                            <ReactCountryFlag
                                countryCode={`${wallet[0]}`}
                                svg
                                style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                title={`${wallet[0]}`}
                            />
                            {wallet[1]} ({wallet[2]})
                        </button>
                    </span>
                ))}
                </li>
            </ul>
        </div>
    );
}
 
export default ShowWallets;