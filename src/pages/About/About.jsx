import React from 'react'
import './About.css'
import Image from '../../assets/happyBuyer_2.jpg'
import { BiCart,BiUserCircle,BiMoney,BiSolidTruck,BiPackage,BiSolidLogIn,BiUpload,BiSolidShoppingBagAlt } from 'react-icons/bi'
import Features from '../../Component/Features/Features'

const About = () => {
  return (
    <div className='about'>
        {/* about section */}
        <div className="aboutSection">
        {/* values srction */}
        <div className="values">
        <h1 className='textContent_1'>About Us</h1>
        <h3 className='textContent_3'>Welcome to BuyShop!</h3>
           <h2>Innovation</h2>
           <p>BuyShop is your trusted platform connecting you to the deals you need effortlessy,making online shopping a seamless experience.
           </p>
           <h2 className='custom'> Customer-Centic</h2>
           <p>We are dedicated to forstering meaningful connections between users and bussinesses by delivering values-driven solution
           </p>
           <h2>Expertise</h2>
           <p>Our team brings years of expertise in retail,ensuring innovation and reliable services tailored to your needs.</p>
           <h2>Integrity</h2>
           <p>At BuyShop,we uphold values like transparency,honesty,and integrity,ensuring a trustworthy environment for all.
           </p>
        </div>
        {/*ABOUT..................... IMAGE*/}
        <img src={Image} alt="" className='aboutImage'/>
        </div>
        {/*FEATURES HOW IT WORKS.......*/}
        <div className="features">
          <h2>How it works</h2>
          <div className="worksection">
            <div className="block">
              
                <BiCart className='howIcon'/> 
                <h3>1:Browse and Select</h3>
                <p>Explore our marketplace to find unique items that catch your eye and add them to cart</p>
                <BiUserCircle className='howIcon'/>
                 <h3>2:Creat your Account</h3>
                 <p>Sign up for an account to make your purchase process seamless and secure.</p>
                <BiMoney className='howIcon'/>
                <h3>3:Payment Options</h3>
                <p>Choose your preferred method for safe and convenient transaction.</p>
                <BiPackage className='howIcon'/>
                <h3>4:Receive Your Item</h3>
                <p>Sit back and relax your purchase item is shipped directly to your address.</p>
            
            </div>
            <div className="block">
              
                <BiSolidLogIn className='howIcon'/> 
                <h3>1:Sign In  to Start Selling</h3>
                <p>Log in into your account to list your products for sale on BuyShop.</p>
                <BiUpload className='howIcon'/>
                 <h3>2:List Your Product</h3>
                 <p>Upload clear images of your product along with a detailed description to attract buyers.</p>
                <BiSolidShoppingBagAlt className='howIcon'/>
                <h3>3:Well Sell Your Product</h3>
                <p>We prioritize the sale of product</p>
                <BiSolidTruck className='howIcon'/>
                <h3>4:We Ship Your Product</h3>
                <p>Once sold package your product nicely,we pick it up and deliver it..</p>
            
            </div>
            
          </div>
          
        </div>
        <Features/>
    </div>
  )
}

export default About