import React, { useState } from 'react'
import jessica from '../../assets/happyBuyer_2.jpg'
import './Profile.css'
import CTA from '../../Component/CTA/CTA';

const Profile = () => {
    const [formData, setFormData] = useState({
        email: 'jessicaking.52@gmail.com',
        phone: '020 7946 0958',
        cardNumber: '4024 6000 0000 0000',
        expiryDate: '01/25',
        cvc: '123'
    });

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Updated Profile:", formData);
    };
  return (
    <div className='profile_container'>
        <h1>Jessica King</h1>
        <img src={jessica} alt="profile" className='profile_image' />
        <div className="info">
            <p>Email: {formData.email}</p>
            <p>Phone: {formData.phone}</p>
        </div>
        <h2>Payment Methods</h2>
        <ul className="payment_list">
            <li>Visa....2246</li>
            <li>MasterCard....3190</li>
        </ul>
      
      
        <h2>Edit Information</h2>
        <form onSubmit={handleSubmit} className="edit_form">
            <h3>Email:<input type="email" name='email' value={formData.email} onChange={handleChange} placeholder='jessicaking.52@gmail.com' required /></h3>
            <h3>Phone<input type="tel" name='phone' value={formData.phone} onChange={handleChange} placeholder='020 7946 0958' required /></h3>
            <h3>Card Number:<input type="text" name='cardNumber' value={formData.cardNumber} onChange={handleChange} placeholder='4024 6000 0000 0000' required /></h3>
            <h3 >Select Payment Method:
            <select name="paymentMethod" value={formData.paymentMethod} onChange={handleChange} className='method'>
                <option value="text">select Payment</option>
                <option value="visa">Visa</option>
                <option value="masterCard">MasterCard</option>
                <option value="paypal">Paypal</option>
               </select>
            </h3>
            <div className="flex_group"><h3>Expiry Date:<input type="text" name='expiryDate' value={formData.expiryDate} onChange={handleChange} placeholder='01/25' required /></h3>
            <h3>CVC:<input type="text" name='cvc' value={formData.cvc} onChange={handleChange} placeholder='123' required /></h3>
           </div>
           <button type='submit'>Save Changes</button>
             
            
        </form>
        <CTA/>
    </div>
  )
}

export default Profile