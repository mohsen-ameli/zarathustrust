import { useTranslation } from "react-i18next";
import useFetch from "./useFetch";

const RequireBanking = () => {
    let { t } = useTranslation()
    let api = useFetch()

    let submit = async e => {
        e.preventDefault()
        let { response, data } = await api("/api/get-banking-info/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "bank_num": e.target.bank_num.value
            })
        })
        
        if (response.status === 200) {
            console.log("data: ", data)
        }
    }

    return (
        <div className="require-banking">
            <div className="card zarathus-card mx-auto">
                <div className="card-body">
                    <h3 className="fw-normal text-center">Please enter your banking information</h3>
                    <hr className="zarathus-hr"></hr>

                    <form onSubmit={e => submit(e)}>
                        {/* Input */}
                        <div className="form-floating flex-grow-1 mb-2">
                            <input id="bank_num" type="text" placeholder=" " className="form-control" autoComplete="off" required={true} />
                            <label>
                                Enter banking info
                            </label>
                        </div>

                        {/* Next */}
                        <button className="neon-button my-2" type="submit">{t("next")}</button>
                    </form>
                </div>
            </div>
        </div>
    );
}
 
export default RequireBanking;