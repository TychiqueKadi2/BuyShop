import React from 'react'
import './Products.css'
import image2 from '../../assets/watches.png';
import image3 from '../../assets/laptops.jpg'
import image4 from '../../assets/phones.jpg'


const Products = () => {
    const products =[
        {name: "smartwatch", image: image2},
        {name: "smartwatch", image: image3},
        {name: "smartwatch", image: image4},
    ];
  return (
    <div className='productsgrid'>
        {products.map((product) =>(
            <div key ={product.name} className="productCard">
                <img src={product.image} alt={product.name} className='productImage' />
            
            </div>
        ))}
    </div>
  )
}

export default Products