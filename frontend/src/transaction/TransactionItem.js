import { Link } from "react-router-dom";
import ShowDate from "../components/ShowDate";

const TransactionItem = ({ item, username, symbol, currency }) => {
    let icon = ""
    let text = ""
    let money = symbol + (item.price).toFixed(2)
    
    if (item.type === "Deposit") {
        icon = "download"
        text = `Deposit for ${username}`
        money = `+${money}`
    } else if (item.type === "Withdraw") {
        icon = "upload"
        text = `Withdraw for ${username}`
        money = `-${money}`
    } else if (item.type === "Cash Out") {
        icon = "piggy-bank"
        money = `+${money}`
        text = `Cash Out for ${username}`
    } else if (item.type === "Transfer") {
        icon = "send-check"
        if (item.person2 === username) { // recieving
            money = `+${money}`
            text = `Transfer from ${item.person} to ${item.person2}`
        } else { // giving
            money = `-${money}`
            text = `Transfer from ${item.person[0]} to ${item.person2}`
        }
    } else if (item.type === "Exchange") {
        icon = "currency-exchange"
        text = `Exchange for ${username}`
        if (item.person[1] === currency) {
            money = `-${money}`
        } else {
            money = `+${symbol}${item.exPrice}`
        }
    }

    return (
        <Link className="list-group-item list-group-item-action" to={`/transactions/${item.id}`} id="history-list">
            {/* Top Date */}
            <div className="d-flex w-100 justify-content-between">
                <h5 className="mb-1">
                    <ShowDate year={item.date[0]} month={item.date[1]} day={item.date[2]} hour={item.date[3]} minute={item.date[4]} seconds={item.date[5]} format="first" />
                </h5>
            </div>

            {/* Text */}
            <p className="my-2 d-flex align-items-center justify-content-start" id="history-card-text">
                <i className={`history-icons bi bi-${icon}`}></i>
                <span className="ms-3">{ text }</span>
                <span className={"ms-auto " + (money.charAt(0) === "-" ? "minus-money" : "plus-money")}>{ money }</span>
            </p>


            {/* Bottom Date */}
            <small style={{color: "rgba(255, 255, 255, 0.7)"}}> 
                <ShowDate year={item.date[0]} month={item.date[1]} day={item.date[2]} hour={item.date[3]} minute={item.date[4]} seconds={item.date[5]} format="second" /> • { item.type }
            </small>
        </Link>
    );
}
 
export default TransactionItem;