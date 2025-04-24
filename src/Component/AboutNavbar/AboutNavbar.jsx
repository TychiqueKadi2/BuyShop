import React,{useState} from 'react'
import { Link, useLocation } from 'react-router-dom';
import { BiHeart,BiX,BiMenu,BiSearch} from 'react-icons/bi';
import SearchBar from '../SearchBar/SearchBar';
import logo from '../../assets/logo.png'
import './AboutNavbar.css'

const AboutNavbar = () => {
      const location = useLocation();
       const [menuOpen , setMenuOpen]= useState(false);
  return (
    <div className='aboutNavbar'>
        <div className="logo">
        <SearchBar /*setSearchQuery={setSearchQuery} *//>
           <img src={logo} alt="logo" className='logos_2' />
  <h1 className='logo_names'>BuyShop</h1>

        </div>
        <div className={`link_navs ${menuOpen ? "active" : ""}`}>
            
        <Link to = "/about" className={location.pathname === "/about" ? "active" : ""}> About</Link>
        <Link to = "/" className={location.pathname === "/home" ? "active" : ""}>Home</Link>
        <Link to = "/shop" className={location.pathname === "/shop" ? "active" : ""}> shop</Link>
        <Link to = "/contact" className={location.pathname === "/contact" ? "active" : ""}> Contact</Link>
        </div>

                <div className="menu_icon"  onClick={() => setMenuOpen (!menuOpen)}>
                      {menuOpen ?<BiMenu className='humberg_3'/> : <BiX className='bix_3'/>  }
                  </div>
                

    </div>
  )
}

export default AboutNavbar