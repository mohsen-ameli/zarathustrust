import { useCallback, useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import { Configuration, PlaidApi, PlaidEnvironments } from "plaid";

const Link = () => {
    const [token, setToken]     = useState(null)
    const [data, setData]       = useState(null)
    const [isLoading, setIsLoading] = useState(true)


    // Configuration for the Plaid client
    const config = new Configuration({
        basePath: PlaidEnvironments[process.env.PLAID_ENV],
        baseOptions: {
        headers: {
            "PLAID-CLIENT-ID": process.env.PLAID_CLIENT_ID,
            "PLAID-SECRET": process.env.PLAID_SECRET,
            "Plaid-Version": "2020-09-14",
        },
        },
    });
  
    //Instantiate the Plaid client with the configuration
    const client = new PlaidApi(config);

    
    let exchange = async () => {
        const tokenResponse = await client.linkTokenCreate({
            user: { client_user_id: process.env.PLAID_CLIENT_ID },
            client_name: "ZarathusTrust",
            language: "en",
            products: ["auth"],
            country_codes: ["US"],
            redirect_uri: process.env.PLAID_SANDBOX_REDIRECT_URI,
          });
        console.log(tokenResponse.data)
    }


    const onSuccess = useCallback(async (publicToken) => {
        setIsLoading(true)
        await fetch("/api/exchange_public_token", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ public_token: publicToken }),
        })
        await getBalance();
    }, []);
    
    
    // Creates a Link token
    const createLinkToken = useCallback(async () => {
        // For OAuth, use previously generated Link token
        if (window.location.href.includes("?oauth_state_id=")) {
            const linkToken = localStorage.getItem('link_token');
            setToken(linkToken);
        } else {
            const response = await fetch("/api/create_link_token", {});
            const data = await response.json();
            setToken(data.link_token);
            localStorage.setItem("link_token", data.link_token);
        }
    }, [setToken]);


    // Fetch balance data
    const getBalance = useCallback(async () => {
        setIsLoading(true);
        const response = await fetch("/api/balance", {});
        const data = await response.json();
        setData(data);
        setIsLoading(false);
    }, [setData, setIsLoading]);


    const config_ = {
        token,
        onSuccess,
    }

    const { open, ready } = usePlaidLink(config_)

    useEffect(() => {
        exchange()
        if (token == null) {
            createLinkToken()
        }
        if (ready) {
            open()
        }
    })

    return (
        <div className="plaid">
            <div>
                <button onClick={() => open()}>Link account</button>
            </div>
        </div>
    );
}
 
export default Link;