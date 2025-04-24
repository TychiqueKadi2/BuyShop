import React,{useState} from 'react'
import { Link, useLocation } from 'react-router-dom';
import { BiHeart,BiX,BiMenu} from 'react-icons/bi';
import profile from '../../assets/happyBuyer.jpg'
import logo from '../../assets/logo.png'
import './SellNavbar.css'

const SellNavbar = () => {
     const location = useLocation();
       const [menuOpen , setMenuOpen]= useState(false);
  return (
    <div className='sellNavbar'>
        <div className="logo">
          <img src={logo} alt="logo" />
          
           <h1 className='logo_namese'>BuyShop</h1>

        </div>
        <div className={`li_nav ${menuOpen ? "active" : ""}`}>
            
        <Link to = "/sell" className={location.pathname === "/sell" ? "active" : ""}> Sell</Link>
        <Link to = "/" className={location.pathname === "/home" ? "active" : ""}>Home</Link>
        <Link to = "/profile" className={location.pathname === "/profile" ? "active" : ""}> Profile</Link>
        
        </div>
        <div className="image_pro">
          <Link to = "/profile" className={location.pathname === "/profile" ? "active" : ""} ></Link><img src={profile} alt="" />
        </div>
        <div className="menu-icones"  onClick={() => setMenuOpen (!menuOpen)}>
           {menuOpen ?<BiMenu className='humberg_4'/> : <BiX className='bix_4'/>  }
           </div>
                        
    </div>
  )
}

export default SellNavbar