import React from 'react'
import callto from '../../assets/happyBuyer.jpg'
import './CTA.css'

const CTA = () => {
  return (
    <div className='cta_container'>
        {/*left section*/}
        <div className="cta_text">
            <h2>save your updates</h2>
            <p>Ensure your profile is up-to-date by saving your changes now. <br/>
            your updates have been successfully applied!
            </p>
            <button className='cta_button'>Join  for free</button>
        </div>
        {/*right section*/}
        <div className="cta_image">
            <img src={callto} alt="team collaboration" />
        </div>
    </div>
  )
}

export default CTA