import { useEffect, useRef, useState } from "react"
import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"

import ReactCountryFlag from "react-country-flag"

import useFetch from "./useFetch"
import persia from '../images/persia.jpg'

const ShowWallets = ({home, changeCurr}) => {
    const [wallets, setWallets] = useState([])

    let link                    = useRef()
    let dropdown                = useRef()
    let api                     = useFetch()
    const { t }                 = useTranslation()
    
    useEffect(() => {
        let loadWallets = async () => {
            let { response, data } = await api("/api/wallets/")
            if (response.status === 200) {
                setWallets(data)
            }
        }; loadWallets()

        // eslint-disable-next-line
    }, [])

    let mouseOver = () => link.current.style.color = "black"
    let mouseOut = () => link.current.style.color = "#f8b119c7"

    return (
        <div className="show-wallets dropdown align-self-center ms-3">

            <Link className="neon-button" to="#" role="button" onMouseOver={() => mouseOver()} onMouseOut={() => mouseOut()}
            id="dropdownMenuLink" data-bs-toggle="dropdown" aria-expanded="false">
                {t("wallets")} <i className="fas fa-caret-down" ref={link}></i>
            </Link>
            
            <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink" ref={dropdown}>
                {home &&
                <>
                    <li><Link className="dropdown-item" to="/wallet-search">{t("make_new_wallet")}</Link></li>
                    <li><hr className="dropdown-divider"></hr></li>
                </>
                }
                {wallets && wallets.map((wallet, i) => (
                    <li key={i}>
                        <Link to="#" name="wallet-post" onClick={() => changeCurr(wallet)}
                            value={wallet[0]} className="dropdown-item">
                            
                            {wallet[0] === "IR" ? 
                            <img alt='' style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}} src={persia} ></img> :
                            <ReactCountryFlag
                                countryCode={`${wallet[0]}`}
                                svg
                                style={{width: '1.5em', lineHeight: '1.5em', marginBottom: '.1em', marginRight: '.5em'}}
                                title={`${wallet[0]}`}
                            />
                            }
                            {wallet[1]} ({wallet[2]})
                        </Link>
                    </li>
                ))}
            </ul>

        </div>
    );
}
 
export default ShowWallets;