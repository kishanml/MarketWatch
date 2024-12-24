import React, { useState, useEffect, useMemo } from "react";
import { FaCaretUp, FaCaretDown } from "react-icons/fa";

const IndexView = ({ instrument, data , title }) => {
  const formatDate = () => {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, "0");
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const year = now.getFullYear();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");

    return `${day}:${month}:${year} ${hours}:${minutes}`;
  };

  const [fallbackPrice, setFallbackPrice] = useState(
    data?.current_price || 9999
  );
  const [fallbackChange, setFallbackChange] = useState(data?.price_change || 0);
  const [currentTime, setCurrentTime] = useState(
    data?.last_datetime || formatDate()
  );
  const [fallbackGval, setFallbackGVal] = useState(
    data?.cpg_value|| 9999
  );
  const [isCESelected, setIsCESelected] = useState(true);

  // Ensure live data updates
  useEffect(() => {
    if (
      data?.current_price !== fallbackPrice ||
      data?.price_change !== fallbackChange ||
      data?.last_datetime !== currentTime ||
      data?.cpg_value !== fallbackGval
    ) {
      setFallbackPrice(data?.current_price || 9999);
      setFallbackChange(data?.price_change || 0);
      setCurrentTime(data?.last_datetime || formatDate());
      setFallbackGVal(data?.cpg_value || 9999)
    }
  }, [data, fallbackPrice, fallbackChange, currentTime,fallbackGval]);

  // Memoize derived values for performance
  const ceData = useMemo(
    () => (data?.call_data?.length > 0 ? data.call_data : null),
    [data]
  );
  const peData = useMemo(
    () => (data?.put_data?.length > 0 ? data.put_data : null),
    [data]
  );
  const selectedData = useMemo(
    () => (isCESelected ? ceData : peData),
    [isCESelected, ceData, peData]
  );

  const handleCEClick = () => setIsCESelected(true);
  const handlePEClick = () => setIsCESelected(false);

  return (
    <div className="flex flex-col gap-4 w-full h-full border-2 border-gray-500 rounded-lg shadow-lg">
      {/* Header Section */}
      <div className="flex justify-center p-3 bg-[#072f3f] text-white rounded-t-lg">
        <h1 className="text-xl font-bold">{title}</h1>
      </div>

      {/* Market Info Section */}
      <div className="flex flex-row gap-x-4 items-center px-5">
        <h1 className="text-3xl font-semibold">{instrument}</h1>
        <h2 className="text-lg font-semibold text-gray-500">
          LTP: <span className="text-green-600 text-2xl">{fallbackPrice}</span>
        </h2>
        <div className="flex items-center gap-1">
          {fallbackChange >= 0 ? (
            <FaCaretUp className="text-green-600" />
          ) : (
            <FaCaretDown className="text-red-600" />
          )}
          <p
            className={`text-base ${
              fallbackChange >= 0 ? "text-green-600" : "text-red-600"
            }`}
          >
            {fallbackChange}
          </p>
        </div>
        <h2 className="text-md font-semibold text-gray-500">
          DateTime:{" "}
          <span className="text-orange-600 text-xl">{currentTime}</span>
        </h2>
        <h2 className="text-md font-semibold text-gray-500">
          Total Gval:{" "}
          <span className={`${fallbackGval>0 ? "text-green-600" : "text-red-600"} text-xl`}>{fallbackGval}</span>
        </h2>
      </div>

      {/* Toggle Buttons */}
      <div className="flex justify-center items-center border-gray-600">
        <button
          className={`px-8 py-2 border-t border-l border-b border-gray-600 rounded-l-lg ${
            isCESelected ? "bg-green-400" : "hover:bg-gray-200"
          }`}
          onClick={handleCEClick}
        >
          CE
        </button>
        <button
          className={`px-8 py-2 border border-gray-600 rounded-r-lg ${
            !isCESelected ? "bg-red-400" : "hover:bg-gray-200"
          }`}
          onClick={handlePEClick}
        >
          PE
        </button>
      </div>

      {/* Table Section */}
      <div className="flex flex-col mx-4 overflow-hidden border border-gray-300 rounded-lg mb-10">
        <div className="overflow-auto max-h-[400px] ">
          {/* Set max height for scrollable table body */}
          <table className="min-w-full bg-white">
            <thead className="sticky top-0 bg-gray-200 border-">
              <tr>
                <th className="border border-gray-600 p-2">SlNo.</th>{" "}
                {/* Added Index column */}
                <th className="border border-gray-600 p-2">Instrument</th>
                <th className="border border-gray-600 p-2">Strike</th>
                <th className="border border-gray-600 p-2">Last Price</th>
                <th className="border border-gray-600 p-2">IV</th>
                <th className="border border-gray-600 p-2">OI</th>
                <th className="border border-gray-600 p-2">Gvalue</th>
                <th className="border border-gray-600 p-2">Last Traded Time</th>
                <th className="border border-gray-600 p-2">Expiry Date</th>
                <th className="border border-gray-600 p-2">Volume Traded</th>
                <th className="border border-gray-600 p-2">OI Change</th>
              </tr>
            </thead>
            <tbody>
              {selectedData && selectedData.length > 0 ? (
                selectedData.slice(0, 10).map((item, index) => (
                  <tr key={index} className="hover:bg-gray-100">
                    <td className="border border-gray-600 p-2">{index + 1}</td>
                    <td className="border border-gray-600 p-2">
                      {item.trading_symbol}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.strike}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.last_traded_price}
                    </td>
                    <td className="border border-gray-600 p-2">{item.iv}</td>
                    <td className="border border-gray-600 p-2">{item.oi}</td>
                    <td className="border border-gray-600 p-2">
                      {item.Gvalue}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.last_trade_time}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.expiry}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.volume_traded}
                    </td>
                    <td className="border border-gray-600 p-2">
                      {item.oi_change}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="11"
                    className="text-center border border-gray-600 p-2 text-gray-500 font-semibold"
                  >
                    No Data Yet
                  </td>
                </tr>
              )}
              {/* Make remaining rows scrollable */}
              {selectedData && selectedData.length > 10
                ? selectedData.slice(10).map((item, index) => (
                    <tr key={index + 10} className="hover:bg-gray-100">
                      <td className="border border-gray-600 p-2">
                        {index + 11}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.trading_symbol}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.strike}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.last_traded_price}
                      </td>
                      <td className="border border-gray-600 p-2">{item.iv}</td>
                      <td className="border border-gray-600 p-2">{item.oi}</td>
                      <td className="border border-gray-600 p-2">
                        {item.Gvalue}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.last_trade_time}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.expiry}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.volume_traded}
                      </td>
                      <td className="border border-gray-600 p-2">
                        {item.oi_change}
                      </td>
                    </tr>
                  ))
                : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default IndexView;
