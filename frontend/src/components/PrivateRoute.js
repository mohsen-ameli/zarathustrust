import { Route, Redirect } from 'react-router-dom'
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'

const PrivateRoute = ({ comp: Component, ...rest }) => {
    let { user } = useContext(AuthContext)

    return (
        <Route {...rest} render={props => !user ? <Redirect to="/login" /> : <Component {...props} />}/>
    )
}

export default PrivateRoute;