import React from 'react'
import { BiSearch } from 'react-icons/bi'
import './SearchBar.css'

const SearchBar = () => {

  return (
    <div className='searchContainer'>
        <BiSearch className='search'/>
        <input type="text"
        placeholder='search...' /*onChange={(e)
            => setSearchQuery (e.target.value)} */ />
    </div>
  )
}

export default SearchBar