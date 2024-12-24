import React, { useState } from "react";
import { FaHome } from "react-icons/fa";
import { Link, useLocation } from "react-router-dom";

const ErrorPage = () => {
  const location = useLocation();
  const errorMsg = location.state?.errorData || {};
  const [devMsg, setDevMsg] = useState(false);

  return (
    <div className="bg-[#041d27] text-white">
      <Link to="/">
        <div className="flex flex-row gap-2 pt-2 pl-5">
          <FaHome style={{ height: "30px", width: "30px" }} />
        </div>
      </Link>
      <div className="flex justify-center items-center flex-col m-auto h-screen">
        <h1 className="text-6xl mb-20">Error Occurred</h1>
        <h3 className="text-2xl ">
          {errorMsg.error || "An unknown error occurred."}
        </h3>
        <label className="flex flex-row gap-4 text-white mt-10">
          <input
            type="checkbox"
            className="h-5 w-5"
            checked={devMsg}
            onChange={(e) => setDevMsg(e.target.checked)}
          />
          Show Developer Message
        </label>
        {devMsg && errorMsg.exception && (
          <div className="flex p-4 text-white mt-10 mx-24 border-2 border-gray-600">
            <p>{errorMsg.exception}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorPage;
