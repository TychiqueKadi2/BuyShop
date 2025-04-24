import React from 'react'
import { Link } from 'react-router-dom'
import './Hero.css'

const Hero = () => {
  return (
    <div className='hero'>
        <div className="text">
        <h1>Welcome To BuyShop</h1>
        <p className='content'>Your trusted marketplace for selling or buying preowned goods at great prices. Whether you are looking tor quick cash or just to upgrade this is the place for you.</p>
        </div>
        <div className="hero_buttons">
           <Link to="/shop" className='Link'><button className="buttons_b">Buy</button></Link>
           <Link to = "/sell" className='Link'><button className="buttons_s">Sell</button></Link>
        </div>
    </div>
  )
}

export default Hero