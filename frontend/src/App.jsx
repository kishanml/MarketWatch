
import * as React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginHome from "./components/LoginHome";
import HomePage from "./components/HomePage";
import ErrorPage from "./components/ErrorPage";
import WebSocketTest from "./components/WebSocketTest";


const App = () => {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<LoginHome/>}></Route>
      <Route path="/home" element={<HomePage/>}></Route>
      <Route path="/error" element={<ErrorPage/>}></Route>
      {/* <Route path="/test" element={<WebSocketTest/>}></Route> */}

      
      </Routes>
    </BrowserRouter>
  )
}

export default App