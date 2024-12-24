import React, { useEffect, useState } from "react";
import { CgProfile } from "react-icons/cg";
import { Link, useLocation } from "react-router-dom";
import { CiSearch } from "react-icons/ci";
import IndexView from "./IndexView";
import NewsScroller from "./NewsScroller";
import io from "socket.io-client";

const socket = io("http://localhost:5000");

const HomePage = () => {
  const location = useLocation();
  const details = location.state?.viewData || {};

  // use states
  const [data, setData] = useState([]);
  const [searchInput, setSearchInput] = useState(""); // By default call NIFTY
  const [instrument, setInstrument] = useState("NIFTY"); // Start with "NIFTY"
  
  useEffect(() => {
    // Send the selected instrument to the server and fetch the data
    sendDataToServer(instrument);

    socket.on("stock_data", (stockData) => {
      if (stockData) {
        const parsedData = JSON.parse(stockData);
        setData(parsedData);
        console.log("Received data:", parsedData);
      }
    });

    return () => {
      socket.off("stock_data");
    };
  }, [instrument]); 


  const sendDataToServer = (instrument) => {
    socket.emit("send_data", { instrumentNames: [instrument] });
  };

  const handleSearch = () => {
    const upperCaseInput = searchInput.toUpperCase();
    setSearchInput(upperCaseInput); 
    setInstrument(upperCaseInput); 
    setData({"call_data":[],"put_data":[],"current_price":9999,"price_change":0});

  };


  return (
    <div>
    <section id="navBar" className="flex flex-row justify-between text-white p-5 bg-[#041d27]">
      <Link to="/">
        <h2>MarketWatch</h2>
      </Link>
      {details.user_name ? (
        <h1>Welcome {details.user_name}!</h1>
      ) : (
        <h1>Welcome trader!</h1>
      )}
      <CgProfile className="cursor-pointer" style={{ height: "25px", width: "25px" }} />
    </section>
  
    <div id="searchBar" className="flex justify-center items-center my-5">
      <div className="flex flex-row gap-2 p-3 border-2 w-[90%] sm:w-[70%] lg:w-[50%] border-gray-600 rounded-xl">
        <CiSearch style={{ height: "25px", width: "25px" }} />
        <input
          className="outline-none w-full"
          type="text"
          placeholder="Search for Instrument"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <button
          className="border-l px-2"
          onClick={handleSearch}
        >
          Enter
        </button>
      </div>
    </div>
  
    {/* <div
      className={`flex flex-col sm:flex-row ${
        instrument === "NIFTY" || instrument === "BANKNIFTY" ? "justify-between" : "justify-center"
      } gap-4 px-5`}
      style={{ height: "calc(100vh - 150px)" }} 
    >
      <div
        className={`${
          instrument === "NIFTY" || instrument === "BANKNIFTY" ? "w-full mx-2 sm:w-[70%]" : "w-full"
        }`}
      >
        <IndexView instrument={instrument} data={data} />
      </div>
  
      {(instrument === "NIFTY" || instrument === "BANKNIFTY") && (
        <div className="w-full sm:w-[37%] overflow-auto">
          <NewsScroller />
        </div>
      )}
    </div> */}
     <div
      className={`flex flex-col sm:flex-row justify-center gap-4 px-5`}
      style={{ height: "calc(100vh - 150px)" }} 
    >
      <div
        className={`w-full`}
      >
        <IndexView instrument={instrument} data={data} />
      </div>

    </div>
  </div>
  
  );
};

export default HomePage;
