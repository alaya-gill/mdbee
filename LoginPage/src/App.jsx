import Login from "./Component/Login/Login";
import Navbar from "./Component/Navbar/Navbar";
import OTP from "./Component/OTP/OTP";
import "./App.css";
import { Route, Routes } from "react-router-dom"; // Import BrowserRouter
import SignUp from "./Component/SignUp/Signup";
import SetPassword from "./Component/Set-Password/set-password";
import Users from "./Component/Users/users";

function App() {
  return (
    <div className="App">
      <Navbar />

      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/otp" element={<OTP />} />
        <Route path="/set-new-password/:uid/:token" element={<SetPassword />} />
        <Route path="/users" element={<Users />} />
      </Routes>
    </div>
  );
}

export default App;
