
import React, { useState } from 'react'
import './Sell.css'
import Finalise from '../../Component/Finalise/Finalise';
import FAQ from '../../Component/FAQ/FAQ';

const Sell = () => {
    const[image, setImage] = useState(null);
    const handleImageUpload = (event) => {
        setImage(URL.createObjectURL (event.target.file[0]));

    };
  return (
    <div className='sellItem'>
        <h2>Sell Your Item</h2>
        {/*image upload */}
        <div className="uploadSection">
            <label>upload</label>
            <input type="file" accept='image/*' onChange={handleImageUpload}/>
            {image && <img src={image} alt="Preview" className='previewImage'/>}
        </div>
        <div className="itemDetails">
            <label>Detailed Description:</label>
            <textarea placeholder='Enter item deatils here...'/>

            <label>Brand:</label>
            <select>
                <option>Select a Brand</option>
                <option>Apple</option>
                <option>Samsung</option>
                <option>Nike</option>
                <option>Oppo</option>
            </select>
            <label>Price ($):</label>
            <input type="number" placeholder='Enter price' />
        </div>
        <Finalise/>
        <FAQ/>

    </div>
  )
}

export default Sell