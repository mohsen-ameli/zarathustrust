import useFetch from "../components/useFetch";

const AccountPage = () => {
    const { data: acc, isLoading, error } = useFetch("/api/accounts/")
    console.log(acc)

    return (
        <div className="account-page">
            { isLoading && <div>Loading...</div> }
            { error && <div>{ error }</div> }
            { acc && acc.map(data => (
                <div className="" key={data.id}>{data.created_by} - {data.total_balance} | {data.main_currency}</div>
            )) }
        </div>
    );
}
 
export default AccountPage;