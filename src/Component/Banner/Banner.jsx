import React from 'react'
import './Banner.css'
import { BiCart } from 'react-icons/bi'
import bannerImage from '../../assets/happyBuyer.jpg'

const Banner = () => {
  return (
    <div className='banner'>
        <div className="bannerContent">
            <h2 className="bannerTitle">
                Seasonal Sale Extravaganza
            </h2>
           <h1 className='free_contents'>FREE DELIVERY!!</h1>
            <button className="bannerButton"> <BiCart className='cartBtn'/> Shop Now!</button>
        </div>
        <img src={bannerImage} alt="sale Banner"  className='bannerImage'/>
    </div>
  )
}

export default Banner