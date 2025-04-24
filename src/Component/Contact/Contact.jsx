import React, { useState } from 'react'
import { BiPhone,BiEnvelope,BiUser, BiLocationPlus } from 'react-icons/bi';
import './Contact.css'

const Contact = () => {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        message: ''
    });

    const handleChange = (e) => {
        setFormData({...FormData, [e.target.name]: e.target.value});
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Form Submitted:", formData);
    };
  return (
    <div className='contact_container'>
        <div className="contact_info">
            <h2>Contact Us</h2>
            <p>Feel free to use the form to drop us an email.Old fashioned phone calls work too.</p>
            <div className="info_item">{<BiPhone  className='contact_icons'/>} <p>0123456789</p></div>
            <div className="info_item">{<BiEnvelope  className='contact_icons'/>} <p>info@butshop.com</p></div>
            <div className="info_item">{<BiLocationPlus className='contact_icons'/>} <p>Somewhere out there</p></div>
           
          
        </div>
        <form className='contact_form' onSubmit={handleSubmit}>
            <div className="input_group">
                <div className="icons_container">
                    <BiUser className='consIcon'/>
                    <input type="text" name='firstName' placeholder='First Name' onChange={handleChange} required />
                </div>
               <div className="icons_container">
               <BiUser className='consIcon'/>
               <input type="text" name='lastName' placeholder='Last Name' onChange={handleChange} required />
               </div>
                
            </div>
            <div className="icons_container">
                <BiEnvelope className='consIcon'/>
                <input type="email" name='email' placeholder='Email' onChange={handleChange}required />
            </div>
            <div className="icons_container">
                <BiPhone className='consIcon'/>
                <input type="tel" name='phone' placeholder='Phone Number' onChange={handleChange}required />
                
            </div>
        
            <textarea name="message" placeholder='Your Message' onChange={handleChange} required />
          
            <button type="submit" className='contact_btn'>Submit</button>
        </form>
    </div>
  )
}

export default Contact