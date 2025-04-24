import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom';
import { BiHeart,BiX,BiMenu,BiSearch} from 'react-icons/bi';
import SearchBar from '../SearchBar/SearchBar';
import logos from '../../assets/logo.png'
import './ShopNavbar.css'

const ShopNavbar = () => {
    const location = useLocation();
    const [menuOpen , setMenuOpen]= useState(false);
  return (
    <div className='shopnavbar'>
        <div className="logo">
        <SearchBar className='search_2' /*setSearchQuery={setSearchQuery} *//>
           
            <Link to = "/" className={location.pathname === "/home" ? "active" : ""}> <img src={logos} alt="logo" className='logos_1' /></Link>
            <h1 className='logo_nameses'>BuyShop</h1>

        </div>
        <div className={`link_nave ${menuOpen ? "active" : ""}`}>
        <Link to = "/shop"  onClick={ () => setMenuOpen (false)} className={location.pathname === "/shop" ? "active" : ""}> Shop</Link>
        <Link to = "/shop"  onClick={ () => setMenuOpen (false)} className={location.pathname === "/catergory" ? "active" : ""}>Catergory</Link>
        <Link to = "/shop"  onClick={ () => setMenuOpen (false)} className={location.pathname === "/deal" ? "active" : ""}> Deal</Link>
        </div>
        <BiSearch className='searcher_bair'/>
        <div className="menu-icon"  onClick={() => setMenuOpen (!menuOpen)}>
              {menuOpen ?<BiMenu className='humberg'/> : <BiX className='bix'/>  }
          </div>
        
    </div>
  )
}

export default ShopNavbar