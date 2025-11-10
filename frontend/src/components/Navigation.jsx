import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Navigation() {
    const location = useLocation()

    return (
        <nav className="nav">
            <div className="nav-container">
                <Link to="/" className="nav-brand">
                    SafeEatsNYC
                </Link>
                <div className="nav-links">
                    <Link 
                        to="/" 
                        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                    >
                        Home
                    </Link>
                    <Link 
                        to="/about" 
                        className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
                    >
                        About Us
                    </Link>
                </div>
            </div>
        </nav>
    )
}

