import React from 'react'
import './Features.css'
import { BiUser,BiShieldAlt,BiSearch,BiArrowFromRight} from 'react-icons/bi'

const Features = () => {
  return (
    <div className='features'>
        <h2>Blog</h2>
        <div className="featuregrid">
            {/*user-friendly */}
            <div className="featurecard">
                <BiUser className='featureIcon'/>
                <h3>User-Friendly UI</h3>
                <h4>Interface Design</h4>
                <p>Navigate effortlessly with an intuitive and visually appealing design that enhances the shopping experinces.</p>
                <BiArrowFromRight className='arrowRIcon'/>
            </div>
            {/* secure payment */}
            <div className="featurecard">
                <BiShieldAlt className='featureIcon'/>
                <h3>Secure Payment</h3>
                <h4>Transction Safety</h4>
                <p>Enjoy peace of mind with robust encryption and multy-layered security of all your transaction.</p>
                <BiArrowFromRight className='arrowRIcon'/>
            </div>
            {/* advanced search */}
            <div className="featurecard">
                <BiSearch className='featureIcon'/>
                <h3>Advanced Search</h3>
                <h4>Search Optimization</h4>
                <p>Quickly find products with smart filters, predictive text,and personalized search results.</p>
                <BiArrowFromRight className='arrowRIcon'/>
            </div>
            
        </div>
        {/* explore features button */}
        <button className="explorebutton">Read more</button>
    </div>
  )
}

export default Features