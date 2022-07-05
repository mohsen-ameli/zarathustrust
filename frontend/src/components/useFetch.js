import { useContext } from 'react'
import jwt_decode from "jwt-decode";
import dayjs from 'dayjs'
import AuthContext from '../context/AuthContext';


let useFetch = () => {
    let config = {}

    let {authToken, setAuthToken, setUser, logoutUser} = useContext(AuthContext)


    let originalRequest = async (url, config)=> {
        url = `${url}`
        let data = ""
        let response = await fetch(url, config)
        try {
            data = await response.json()   
        } catch (error) {
            ;
        }
        return {response, data}
    }

    let refreshToken = async (authToken) => {
        let response = await fetch('/api/token/refresh/', {
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({'refresh':authToken.refresh})
        })

        if (response.status === 200) {
            let data = await response.json()
            localStorage.setItem('authToken', JSON.stringify(data))
            setAuthToken(data)
            setUser(jwt_decode(data.access))
            return data
        } else {
            logoutUser()
        }
    }

    let callFetch = async (url, conf) => {
        config['method'] = conf?.method
        config['body'] = conf?.body

        const user = jwt_decode(authToken?.access)
        const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;

        if(isExpired){
            authToken = await refreshToken(authToken)
        }

        config['headers'] = {
            Authorization:`Bearer ${authToken?.access}`,
            'X-CSRFToken':conf?.headers
        }

        let {response, data} = await originalRequest(url, config)
        return {response, data}
    }

    return callFetch
}

export default useFetch;