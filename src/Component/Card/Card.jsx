import React from 'react'
import './card.css'
import product from '../Card'

const Card = () => {
  return (
    <div className='card_container'>
        {product.map((products, id)=>(
        <div className="card" key={id}>
            <div className="card_img">
                <img src={products.image} alt="" />
            </div>
            <div className="card_name">
                <h3>{products.name}</h3>
                <p>{products.price}</p>
            </div>
            <div className="card_btn">
                <p>Buy Now</p>
            </div>
        </div>
        ))}
       
    </div>
  )
}

export default Card