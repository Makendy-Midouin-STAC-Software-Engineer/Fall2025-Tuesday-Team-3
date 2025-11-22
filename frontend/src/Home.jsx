import React from 'react'
import { useNavigate } from 'react-router-dom'
import './styles.css'

// Helper to get correct image path for production (with /static/ prefix) or development
const getImagePath = (imageName) => {
    // In production, Vite sets base to /static/, so we need /static/ prefix
    // In development, base is /, so we can use / directly
    const isProduction = import.meta.env.PROD
    if (isProduction) {
        return `/static/${imageName}`
    }
    return `/${imageName}`
}

export default function Home() {
    const navigate = useNavigate()

    return (
        <div className="home-page">
            <header className="home-header">
                <div className="home-header-content">
                    <h1 className="home-logo">SafeEats<span className="logo-nyc">NYC</span></h1>
                    <p className="home-tagline">Know before you dine</p>
                </div>
            </header>

            <section className="hero-section">
                <div className="hero-image-container">
                    <img 
                        src={getImagePath("placeholder-nyc-skyline.jpg")} 
                        alt="NYC Skyline" 
                        className="hero-image"
                    />
                    <div className="hero-overlay">
                        <h2 className="hero-title">Find Safe Dining in the City</h2>
                        <p className="hero-description">
                            Our SafeEats star ratings help you make informed choices about where to eat in New York City.
                            Every rating is based on real inspection data from the NYC Department of Health.
                        </p>
                        <button
                            className="hero-cta"
                            onClick={() => navigate('/explore')}
                            aria-label="Explore restaurants"
                        >
                            Search Restaurants
                        </button>
                    </div>
                </div>
            </section>

            <section className="features-section">
                <div className="features-container">
                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <img 
                                src={getImagePath("placeholder-nyc-restaurant.jpg.jpg")} 
                                alt="NYC Restaurant" 
                                className="feature-image"
                            />
                        </div>
                        <h3 className="feature-title">Real Inspection Data</h3>
                        <p className="feature-text">
                            Our 1–4 star ratings are calculated from actual NYC health department inspections, 
                            tracking violations and cleanliness over time.
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <img 
                                src={getImagePath("placeholder-nyc-street.jpg.jpg")} 
                                alt="NYC Street Scene" 
                                className="feature-image"
                            />
                        </div>
                        <h3 className="feature-title">Search by Borough</h3>
                        <p className="feature-text">
                            Filter restaurants across all five boroughs—Manhattan, Brooklyn, Queens, 
                            the Bronx, and Staten Island.
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon-wrapper">
                            <img 
                                src={getImagePath("placeholder-nyc-food.jpg.jpg")} 
                                alt="NYC Food Scene" 
                                className="feature-image"
                            />
                        </div>
                        <h3 className="feature-title">Cuisine Filters</h3>
                        <p className="feature-text">
                            Find exactly what you're craving. Search by cuisine type and see 
                            safety ratings for every restaurant.
                        </p>
                    </div>
                </div>
            </section>

            <footer className="home-footer">
                <p>Data sourced from <a href="https://data.cityofnewyork.us" target="_blank" rel="noopener noreferrer">NYC Open Data</a></p>
            </footer>
        </div>
    )
}
