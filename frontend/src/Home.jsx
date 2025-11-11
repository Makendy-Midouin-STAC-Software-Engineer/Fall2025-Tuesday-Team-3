import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, MapPin, Search } from 'lucide-react'
import './styles.css'

export default function Home() {
    const navigate = useNavigate()

    return (
        <div className="container">
            <header className="header">
                <h1 className="title">SafeEatsNYC</h1>
            </header>

            <section className="home-hero">
                <h2 className="home-heading">NYC restaurant inspections made simple</h2>
                <p className="home-subtitle">
                    Explore SafeEats star ratings and violation histories to quickly find safe dining options near you.
                </p>
                <button
                    className="explore-btn-lg"
                    onClick={() => navigate('/explore')}
                    aria-label="Explore restaurants"
                >
                    Start Exploring
                </button>
            </section>

            <section className="home-features">
                <div className="home-feature">
                    <ShieldCheck className="home-icon" aria-hidden="true" />
                    <h3 className="home-feature-title">Transparent Safety</h3>
                    <p className="home-feature-desc">See 1–4★ SafeEats ratings backed by deterministic rule checks.</p>
                </div>
                <div className="home-feature">
                    <Search className="home-icon" aria-hidden="true" />
                    <h3 className="home-feature-title">Powerful Search</h3>
                    <p className="home-feature-desc">Filter by borough or cuisine and sort by star rating or name.</p>
                </div>
                <div className="home-feature">
                    <MapPin className="home-icon" aria-hidden="true" />
                    <h3 className="home-feature-title">NYC Coverage</h3>
                    <p className="home-feature-desc">Up-to-date inspection data sourced from NYC Open Data.</p>
                </div>
            </section>
        </div>
    )
}


