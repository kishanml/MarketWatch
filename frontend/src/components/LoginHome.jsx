import React, { useState } from "react";
import { ThreeDots } from "react-loader-spinner";
import ErrorPage from "./ErrorPage";
import { useNavigate } from "react-router-dom";

const LoginHome = () => {
  const [OpenLoader, setOpenLoader] = useState(false);
  const navigate = useNavigate();

  const handleClick = () => {
    setOpenLoader(true);

    fetch("http://127.0.0.1:5000/login")
      .then(async (response) => {
        const data = await response.json();
        if (response.ok & data.success) {
          navigate("/home", { state: { viewData: data } });
        } else {
          navigate("/error", { state: { errorData: data } });
        }
      })
      .catch((error) => {
        // TODO : direct error to error page
        console.error("There was an error!", error);
      })
      .finally(() => {
        setOpenLoader(false);
      });
  };

  return (
    <section>
      <div className="flex justify-center flex-col m-auto h-screen bg-[#041d27]">
        <h1 className="text-6xl mx-auto mb-10 font-extrabold text-white">
          MARKETWATCH
        </h1>
        <h3 className="text-center mb-10 text-xl text-neutral-300">
        Empower your investments with live insights and analysis.
        </h3>

        <button
          onClick={handleClick}
          className="mx-auto bg-white px-8 text-gray-900 py-2 rounded-md border-gray-800 border-4 hover:bg-green-500 hover:text-white"
        >
          {OpenLoader ? (
            <ThreeDots
              visible={true}
              height="40"
              width="50"
              color="#000000"
              radius="9"
              ariaLabel="three-dots-loading"
              wrapperStyle={{}}
              wrapperClass=""
            />
          ) : (
            <span className="text-lg tracking-wide font-semibold">
              GET STARTED
            </span>
          )}
        </button>
      </div>
    </section>
  );
};

export default LoginHome;
