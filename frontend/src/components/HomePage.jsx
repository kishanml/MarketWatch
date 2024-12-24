import React, { useEffect, useState } from "react";
import { CgProfile } from "react-icons/cg";
import { Link, useLocation } from "react-router-dom";
import { CiSearch } from "react-icons/ci";
import IndexView from "./IndexView";
import NewsScroller from "./NewsScroller";
import io from "socket.io-client";

// Connect to socket server
const socket = io("http://localhost:5000");

const HomePage = () => {
  const location = useLocation();
  const details = location.state?.viewData || {};

  // use states
  const [data, setData] = useState([]);
  const [searchInput, setSearchInput] = useState(""); // Default instrument is NIFTY
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

  // Send selected instrument to server
  const sendDataToServer = (instrument) => {
    socket.emit("send_data", { instrumentNames: [instrument] });
  };

  const whichOptions = (instrument) => {
    let title = "Stock Options";
    if (instrument === "NIFTY" || instrument === "BANKNIFTY") {
      title = "Index Options"; // Corrected assignment here
    }
    return title;
  };

  // Handle search input change
  const handleSearch = () => {
    const upperCaseInput = searchInput.toUpperCase();
    setSearchInput(upperCaseInput);
    setInstrument(upperCaseInput);
    setData({
      call_data: [],
      put_data: [],
      current_price: 9999,
      price_change: 0,
    }); // Reset data on search
  };

  return (
    <div className="bg-[#f4f4f4] min-h-screen">
      {/* Navbar Section */}
      <section
        id="navBar"
        className="flex justify-between items-center text-white p-5 bg-[#041d27] shadow-md"
      >
        <Link to="/">
          <h2 className="text-2xl font-semibold hover:text-[#ff6347] transition duration-300">
            MarketWatch
          </h2>
        </Link>
        <h1 className="text-lg font-semibold">
          {details.user_name
            ? `Welcome, ${details.user_name}!`
            : "Welcome, trader!"}
        </h1>
        <CgProfile
          className="cursor-pointer hover:text-[#ff6347] transition duration-300"
          style={{ height: "30px", width: "30px" }}
        />
      </section>

      {/* Search Bar */}
      <div id="searchBar" className="flex justify-center items-center my-5">
        <div className="flex flex-row gap-2 p-2 border-2 w-[90%] sm:w-[70%] lg:w-[50%] border-gray-600 rounded-xl shadow-md hover:shadow-lg transition duration-300">
          <CiSearch
            style={{ height: "35px", width: "25px" }}
          />
          <input
            className="outline-none w-full text-lg px-2 py-1 rounded-lg"
            type="text"
            placeholder="Search for Instrument"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            className="bg-[#041d27] text-white px-4 py-2 rounded-lg  transition duration-300"
            onClick={handleSearch}
          >
            Enter
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col sm:flex-row justify-center gap-4 px-5 mb-10">
        <div className="w-full sm:w-[70%]">
          <IndexView instrument={instrument} data={data} title={whichOptions(instrument)} />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
