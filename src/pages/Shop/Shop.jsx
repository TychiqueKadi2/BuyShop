import React from 'react'
import './Shop.css'
import Card from '../../Component/Card/Card'
import Banner from '../../Component/Banner/Banner'

const Shop = () => {
  /*
   const {searchQuery, setSearchQuery}= useState ("");
      /* FILTER PRODUCTS */
      /*
      const filterProduct = product.filter ((product) =>
          product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  */

  return (
    <div className='shop_container'>
      <div className="heading_text">
        <h1>featured products</h1>
       
      </div>
      <div className="card_holder">
    {/*  {filteredProduct.map((product) =>(
                  <Card/>
              ))}
                  */}
        <Card/>
      </div>
      <div className="banner_holder">
        <Banner/>
      </div>
    </div>
  )
}

export default Shop