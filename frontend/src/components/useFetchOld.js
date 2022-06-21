import { useState, useEffect, useContext } from "react";
import axios from "axios";
import AuthContext from "../context/AuthContext";
import useAxios from "./useAxios";

const useFetchOld = (url) => {
  const [data, setData] 			= useState(null);
  const [isLoading, setIsLoading] 	= useState("Loading...");
  const [error, setError] 			= useState(null);
  let api 							= useAxios()

  useEffect(() => {
	api.get(url)
	.then(res => {
		setIsLoading(false);
		setData(res.data);
	})
	.catch(() => {setIsLoading(false); setError("An error occurred. Awkward..");});
	}, [url]);

	return { data, isLoading, error };
};

export default useFetchOld;
