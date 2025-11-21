import React from "react";
import styled from "styled-components";
import bread from "../assets/bread.png";
import Footer from "../Footer/Footer";

const Form = () => {
  return (
    <StyledWrapper>
      <div className="container">
        <input type="checkbox" id="signup_toggle" />
        <form className="form">
          <div className="form_front">
            <img src={bread} alt="Bread Icon" className="login-image" />
            <div className="form_details">Login</div>
            <input placeholder="Username" className="input" type="text" />
            <input placeholder="Password" className="input" type="password" />
            <button className="btn">Login</button>
            <span className="switch">
              Don't have an account?{" "}
              <label className="signup_tog" htmlFor="signup_toggle">
                Sign Up
              </label>
            </span>
          </div>

          <div className="form_back">
            <img src={bread} alt="Bread Icon" className="login-image" />
            <div className="form_details">Sign Up</div>
            <input placeholder="Firstname" className="input" type="text" />
            <input placeholder="Username" className="input" type="text" />
            <input placeholder="Password" className="input" type="password" />
            <input
              placeholder="Confirm Password"
              className="input"
              type="password"
            />
            <button className="btn">Sign Up</button>
            <span className="switch">
              Already have an account?{" "}
              <label className="signup_tog" htmlFor="signup_toggle">
                Sign In
              </label>
            </span>
          </div>
        </form>
      </div>
    </StyledWrapper>
  );
    <Footer />
};

const StyledWrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Centers vertically */
  background-color: #D0D9C7; /* matches your project theme */
  perspective: 1200px; 

  .container {
    position: relative;
    width: 350px;
    height: 450px;
  }

  .form {
    position: relative;
    width: 120%;
    height: 120%;
    transform-style: preserve-3d;
    transition: transform 1s ease;
  }
.login-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 12px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

  #signup_toggle {
    display: none;
  }

  #signup_toggle:checked + .form {
    transform: rotateY(180deg);
  }

  .form_front{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 20px;
    background-color: #212121;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6),
      inset 2px 2px 10px rgba(0, 0, 0, 1),
      inset -1px -1px 5px rgba(255, 255, 255, 0.2);
    backface-visibility: hidden;
  }
  .form_back {
    position: absolute;
    width: 110%;
    height: 110%;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 15px;
    background-color: #212121;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6),
      inset 2px 2px 10px rgba(0, 0, 0, 1),
      inset -1px -1px 5px rgba(255, 255, 255, 0.2);
    backface-visibility: hidden;
    padding-top: 20px;
  }

  .form_back {
    transform: rotateY(180deg);
  }

  .form_details {
    font-size: 30px;
    font-weight: 700;
    color: white;
  }

  .input {
    width: 85%;
    height: 50px;
    color: #fff;
    outline: none;
    transition: 0.35s;
    padding: 0 15px;
    background-color: #2c2c2c;
    border-radius: 6px;
    border: 2px solid #212121;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8),
      inset 1px 1px 6px rgba(255, 255, 255, 0.2);
  }

  .input::placeholder {
    color: #999;
  }

  .input:focus {
    transform: scale(1.05);
    box-shadow: 0 0 10px #c9a48b;
  }

  .btn {
    padding: 10px 35px;
    cursor: pointer;
    background-color: #fec195;
    border-radius: 6px;
    border: none;
    color: #212121;
    font-size: 15px;
    font-weight: bold;
    transition: all 0.3s ease;
  }

  .btn:hover {
    background-color: #a8c3b9;
    color: black;
    transform: scale(1.05);
  }

  .switch {
    font-size: 13px;
    color: white;
  }

  .signup_tog {
    font-weight: 700;
    cursor: pointer;
    text-decoration: underline;
    color: #c9a48b;
  }
    .switch {
     margin-top: 10px;
     margin-bottom: 25px;
    }
`;

export default Form;
