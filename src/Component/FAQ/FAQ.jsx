import React, { useState } from 'react'
import {BiChevronUp,BiChevronDown} from 'react-icons/bi'
import './FAQ.css'

const FAQ = () => {
    const [activeIndex, setActiveIndex] = useState(null);

    const questions =[
        {
            question: " how do i list an item for sale?",
            answer: "To list an item, click on the 'sell' button, fill in the item details",
        },
        {
            question: "are the any fees for listing items?",
            answer: ""
        },
        {
            question: "how can i edit or delete my listing",
            answer: ""
        },
        {
            question: "what type of items are prohibited?",
            answer:""
        },
        {
            question: " how do i ensure my listing gets more views?",
            answer:""
        }
    ];
    const handleToggle = (index) => {
        setActiveIndex(activeIndex === index ? null : index);
    }
  return (
    <div className='faq'>
        <h1>Friendly asked questions</h1>
        <p>find answers to common questions about listing items on TradeHub.</p>
        <div className="faq_list">
            {questions.map((item, index) => (
               <div key={index} className="faq_item">
                <div className="faq_question" onClick={() => handleToggle(index)}>
                    {item.question}
                    {activeIndex === index ?<BiChevronUp className='up' /> : <BiChevronDown className='down'/> }
                </div>
                {activeIndex === index && <div className='faq_answer'>{item.answer}</div>}
               </div> 
            ))}
        </div>
    </div>
  )
}

export default FAQ