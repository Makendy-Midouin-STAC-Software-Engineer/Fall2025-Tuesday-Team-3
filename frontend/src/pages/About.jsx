import React, { useState } from 'react'

export default function About() {
    const [email, setEmail] = useState('')

    const teamMembers = [
        { name: 'Nick Nikak' },
        { name: 'Collin Bottrill' },
        { name: 'Hassan Naveed' },
        { name: 'Tamara Edmond' }
    ]

    return (
        <div className="container">
            <div className="about-hero">
                <h1 className="about-title">About SafeEatsNYC</h1>
                <p className="about-description">
                    SafeEatsNYC is your trusted companion for making informed dining decisions in New York City. 
                    We provide easy access to official NYC restaurant inspection data, helping you choose safe 
                    and clean establishments for your next meal.
                </p>
            </div>

            <section className="about-section">
                <h2 className="section-title">Our Mission</h2>
                <p className="section-text">
                    We believe that everyone deserves to know the health and safety standards of the restaurants 
                    they visit. Our platform makes NYC's restaurant inspection data accessible, searchable, and 
                    easy to understand, empowering diners to make informed choices about where they eat.
                </p>
            </section>

            <section className="about-section">
                <h2 className="section-title">Meet Our Team</h2>
                <div className="team-grid">
                    {teamMembers.map((member, index) => (
                        <div key={index} className="team-card">
                            <div className="team-avatar">
                                {member.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <h3 className="team-name">{member.name}</h3>
                        </div>
                    ))}
                </div>
            </section>

            <section className="about-section">
                <h2 className="section-title">Contact Us</h2>
                <div className="contact-card">
                    <div className="contact-item">
                        <span className="contact-icon">📧</span>
                        <div>
                            <strong>Email</strong>
                            <p className="contact-detail">contact@safeatsnyc.com</p>
                        </div>
                    </div>
                    <div className="contact-item">
                        <span className="contact-icon">💬</span>
                        <div>
                            <strong>Support</strong>
                            <p className="contact-detail">We typically respond within 24-48 hours</p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="about-section">
                <h2 className="section-title">Subscribe for Updates</h2>
                <p className="section-text">
                    Stay informed with SafeEats NYC! Enter your email below to subscribe for updates on 
                    new features, safety alerts, and community news.
                </p>
                <div className="subscribe-form">
                    <input
                        type="email"
                        className="input"
                        placeholder="Enter your email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        aria-label="Email address"
                    />
                    <button className="button" type="button">
                        Subscribe
                    </button>
                </div>
                <p className="subscribe-note">
                    By subscribing, you agree to receive updates from SafeEatsNYC. We respect your privacy 
                    and will never share your information.
                </p>
            </section>
        </div>
    )
}

