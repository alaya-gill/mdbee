import React, { useEffect } from "react";
import "./navbar.css";
import img from "../../images/logo.png";
const Navbar = () => {
  return (
    <>
      <div className="navbar">
        <img className="img" src={img} alt="" />
      </div>
    </>
  );
};

export default Navbar;
