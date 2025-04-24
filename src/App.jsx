import React from 'react'
import {Routes, Route, Router, useLocation} from 'react-router-dom'
import './App.css'
import Navbar from './Component/Navbar/Navbar'
import Hero from './Component/Hero/Hero'
import Shop from './pages/Shop/Shop'
import Products from './Component/Products/Products'
import Footer from './Component/Footer/Footer'
import ShopNavbar from './Component/ShopNavbar/ShopNavbar'
import About from './pages/About/About'
import Sell from './pages/Sell/Sell'
import Contact from './Component/Contact/Contact'
import AboutNavbar from './Component/AboutNavbar/AboutNavbar'
import SellNavbar from './Component/SellNavbar/SellNavbar'
import Profile from './pages/Profile/Profile'

function App() {
  const location = useLocation ();
  const isShopage = location.pathname === "/shop";
  const isAboutPage = location.pathname === "/about";
  const isSellPage = location.pathname === "/sell";


  return (
    <>
     {isShopage ? <ShopNavbar/> : isAboutPage ? <AboutNavbar/>: isSellPage ? <SellNavbar/>: <Navbar/>}
    <Routes>
      <Route path = "/" element= {<>
      <Hero/>
      <Products/>
      </>} />
      <Route path="/shop" element={<Shop/>} />
      <Route path="/about" element={<About/>} />
      <Route path="/sell" element={<Sell/>} />
      <Route path="/contact" element={<Contact/>} />
      <Route path="/profile" element={<Profile/>} />
      </Routes>
    <Footer/>
    </>
  );
}


export default App
