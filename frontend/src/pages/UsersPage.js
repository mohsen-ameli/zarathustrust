import useFetch from "../components/useFetch";

const UsersPage = () => {
    const { data: acc, isLoading, error } = useFetch("/api/users/")

    return (
        <div className="users-page">
            { isLoading && <div>Loading...</div> }
            { error && <div>{ error }</div> }
            { acc && acc.map(data => (
                <div className="" key={data.id}>{data.username} - {data.currency} | {data.language}</div>
            )) }
        </div>
    );
}
 
export default UsersPage;