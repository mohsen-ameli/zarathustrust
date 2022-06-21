import { useEffect, useRef, useState } from "react"
import { Link } from "react-router-dom"
import ReactCountryFlag from "react-country-flag"
import useFetch from "./useFetch"

const ShowWallets = ({pk, home, changeCurr}) => {
    const [wallets, setWallets]                     = useState([])
    let link                                        = useRef()
    let api                                         = useFetch()
    
    useEffect(() => {
        loadWallets()
    }, [])


    let loadWallets = async () => {
        let { response, data } = await api(`/api/wallets`)
        if (response.status === 200) {
            setWallets(data)
        } else {
            setError('An error occurred. Awkward..')
            setShowErr(true)
            setIsLoading(false)
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
                Wallets <i className="fas fa-caret-down" ref={link}></i>
            </a>
        
            <ul className="dropdown-menu" aria-labelledby="dropdownMenuLink">

                {home &&<>
                <li><Link className="dropdown-item" to="/wallet-search">Make a New Wallet</Link></li>
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