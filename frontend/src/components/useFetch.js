import { useState, useEffect } from "react";
import axios from "axios";

const useFetch = (url) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState("Loading...");
  const [error, setError] = useState(null);

  useEffect(() => {
	axios.get(url)
		.then((res) => {
			setIsLoading(false);
			setData(res.data);
		})
		.catch(err => {
			setIsLoading(false);
			setError("An error occurred. Awkward..");
		});
	}, [url]);

	return { data, isLoading, error };
};

export default useFetch;
