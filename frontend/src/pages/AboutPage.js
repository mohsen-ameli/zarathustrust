import { Link } from 'react-router-dom';
import useFetch from "../components/useFetch";

const About = () => {
    const { data, isLoading, error } = useFetch('/api/currUser')
    console.log(data)

    return (
    <div className="About">
        <div className="card text-white zarathus-card mx-auto">
            <div className="card-body">
                <h3 className="fw-normal text-center">This is the about page</h3>
                <hr className="zarathus-hr"></hr>
                <h5 className="fw-normal">
                    We Pay You 2% Interest On Your Balance ! Share our website with your friends to get extra prizes.
                </h5>
                <hr className="zarathus-hr"></hr>
                    <Link className="neon-button" to={`/home/${data?.pk}`}>Home</Link>
                <small style={{float: "right"}}>version:0.9.999999999</small>
            </div>
        </div>
    </div>
    );
}
 
export default About;