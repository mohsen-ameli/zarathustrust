import { useEffect } from "react";

const useInterest = (interest, balance, setInterest) => {
    useEffect(() => {
        if (Number(balance) > 0) {
            let int = 0
            let intRate = Number(interest)

            // canceling the delay
            setInterest(intRate.toFixed(20))
            int = Number(balance) * 0.01 / 31536000
            intRate = intRate + int
            // canceling the delay

            const interval = setInterval(() => {
                setInterest(intRate.toFixed(20))

                /* one percent of the total balance per second */
                int = Number(balance) * 0.01 / 31536000
                intRate = intRate + int
            }, 1000);
            return () => {
                clearInterval(interval);
            };
        }
        // eslint-disable-next-line
    }, [interest])

    return (
        <div className="use-interest">
            {interest}
        </div>
    );
}
 
export default useInterest;