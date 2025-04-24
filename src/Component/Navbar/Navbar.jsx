import React, {useState } from 'react'
import  { Link, useLocation} from 'react-router-dom'
import { BiSearch, BiShoppingBag,BiKey,BiMenu,BiX, BiSolidShoppingBag} from 'react-icons/bi' 
import logo from '../../assets/logo.png'
import './Navbar.css'

const Navbar = () => {
  const Location = useLocation();
  const [menuOpen , setMenuOpen]= useState(false);
  return (
    /* main logo */
    <div className='header'>
        <div className="logo">
          <img src={logo} alt="logo" />
            <h1 className='logo_name'>BuyShop</h1>
        </div>
       {/* links navbar */}
        <div className={`navbar ${menuOpen ? "active" : ""}`}>
                <Link  to= "/" onClick={ () => setMenuOpen (false) } className={location.pathname === "/" ? "active" : ""}>Home</Link>
                <Link to = "/shop"  onClick={ () => setMenuOpen (false)} className={location.pathname === "/shop" ? "active" : ""}> Shop</Link>
                <Link to = "/about"  onClick={ () => setMenuOpen (false)} className={location.pathname === "/about" ? "active" : ""}>About</Link>
                <Link to = "/contact" onClick={ () => setMenuOpen (false)} className={location.pathname === "/contact" ? "active" : ""} >Contact</Link>
                <Link to = "/blog" onClick={ () => setMenuOpen (false)} className={location.pathname === "/blog" ? "active" : ""}  >Blog</Link>
        </div>
        <div className="buttons">
           <Link to="/shop" className='Link'><button className='button_sell'><BiKey/> Sell</button></Link>
           <Link to="/shop" className='Link'><button className='button_buy'> <BiSolidShoppingBag/>Buy</button> </Link>
         
        </div>
        <BiSearch className='search_bar'/>
        <div className="menu-icon"  onClick={() => setMenuOpen (!menuOpen)}>
        {menuOpen ?<BiMenu className='humberg_1'/> : <BiX className='bix_1'/>  }
        </div>
    </div>
  )
}

export default Navbar