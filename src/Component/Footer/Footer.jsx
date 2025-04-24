import React from 'react'
import { BiHeart, BiLogoTwitter,BiLogoFacebookCircle,BiLogoLinkedin,BiLogoYoutube } from 'react-icons/bi'
import logo from '../../assets/logo.png'
import './Footer.css'

const Footer = () => {
  return (
    <footer className='footer'>
        <div className='footer-logo'>
            <img src={logo} alt="logo" />
            <h2>BuyShop</h2>
        </div>
        {/*newsletter subscription */}
         <div className="newsletter">
            <p>Subscribe to our newsletter</p>
            <form>
                <input type="email" placeholder='Enter your email' />
                <button type='submit' className='footer_btns'>Subscribe</button>
            </form>
         </div>
         {/* footer links */}
          <div className="footer-links">
            <div className="footer-column">
                <h3>Product</h3>
                <ul>
                    <li><a href="#">Features</a></li>
                    <li><a href="#">Pricing</a></li>
                </ul>
            </div>
            <div className="footer-column">
                <h3>Resources</h3>
                <ul>
                    <li><a href="#">Blog</a></li>
                    <li><a href="#">User</a></li>
                    <li><a href="#">Webinars</a></li>
                </ul>
            </div>
            <div className="footer-column">
                <h3>Company</h3>
                <ul>
                    <li><a href="#">About Us</a></li>
                    <li><a href="#">Contact Us</a></li>
                </ul>
               
            </div>
            <div className="footer-column">
                <h3>Plans & Pricing</h3>
                <ul>
                    <li><a href="#">Personal</a></li>
                    <li><a href="#">Start up</a></li>
                    <li><a href="#">Organization</a></li>
                </ul>
            </div>
          </div>
          {/*footer bottom section */}
          <div className="footer-bottom">
            <select>
                <option value="en">English</option>
            </select>
            <ul>
                <li><a href="#">@ 2025 Brand, Inc.</a></li>
                <li><a href="#">-Privacy</a></li>
                <li><a href="#"> -Terms</a></li>
                <li><a href="#"> -Sitemap</a></li>
            </ul>
            <div className="social-media-icons">
                <a href="#"><BiLogoTwitter className='twitter'/></a>
                <a href="#"><BiLogoFacebookCircle className='facebook'/></a>
                <a href="#"><BiLogoLinkedin className='linkedin'/></a>
                <a href="#"><BiLogoYoutube className='youtube'/></a>
            </div>
          </div>
    </footer>
    
  )
}

export default Footer