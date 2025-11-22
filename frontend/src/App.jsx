import React, { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './styles.css'

const MAX_STARS = 4

const normalizeStarValue = (value) => {
    const numeric = Number(value)
    if (!Number.isFinite(numeric)) {
        return 0
    }
    return Math.max(0, Math.min(MAX_STARS, Math.round(numeric)))
}

const StarDisplay = ({ value, size = 'default' }) => {
    const rating = normalizeStarValue(value)
    if (!rating) {
        return <span className="stars-label muted">No rating</span>
    }

    const starSize = size === 'large' ? '24px' : '18px'
    const labelSize = size === 'large' ? '14px' : '12px'

    return (
        <div className="stars-rating" aria-label={`${rating} out of ${MAX_STARS} stars`}>
            {[...Array(MAX_STARS)].map((_, index) => (
                <span
                    key={index}
                    className={index < rating ? 'star filled' : 'star'}
                    style={{ fontSize: starSize }}
                    aria-hidden="true"
                >
                    ★
                </span>
            ))}
            <span className="stars-label" style={{ fontSize: labelSize }}>{rating} / {MAX_STARS}</span>
        </div>
    )
}

const buildMapsUrl = (address, city, state, zipcode) => {
    const addressParts = [address, city, state, zipcode].filter(Boolean)
    const fullAddress = addressParts.join(', ')
    if (!fullAddress) return null
    // Use Google Maps directions URL
    const encodedAddress = encodeURIComponent(fullAddress)
    return `https://www.google.com/maps/dir/?api=1&destination=${encodedAddress}`
}

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

export default function App() {
    const navigate = useNavigate()
    const [query, setQuery] = useState('')
    const [rawResults, setRawResults] = useState([])
    const [sortOption, setSortOption] = useState('stars_desc')
    const [boroughFilter, setBoroughFilter] = useState('')
    const [cuisineFilter, setCuisineFilter] = useState('')
    const [boroughs, setBoroughs] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [selectedRestaurant, setSelectedRestaurant] = useState(null)
    const [detailLoading, setDetailLoading] = useState(false)

    React.useEffect(() => {
        setBoroughs(['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island'])
    }, [])

    const sortResults = (results, option) => {
        return [...results].sort((a, b) => {
            const aStars = normalizeStarValue(a?.star_rating ?? a?.display_value)
            const bStars = normalizeStarValue(b?.star_rating ?? b?.display_value)
            const aName = a?.name || ''
            const bName = b?.name || ''

            switch (option) {
                case 'stars_asc':
                    if (aStars !== bStars) return aStars - bStars
                    return aName.localeCompare(bName)
                case 'stars_desc':
                    if (aStars !== bStars) return bStars - aStars
                    return aName.localeCompare(bName)
                case 'name_desc':
                    return bName.localeCompare(aName)
                case 'name_asc':
                default:
                    return aName.localeCompare(bName)
            }
        })
    }

    const results = useMemo(() => sortResults(rawResults, sortOption), [rawResults, sortOption])

    const buildSearchParams = (baseQuery) => {
        const params = new URLSearchParams({ q: baseQuery || '*', display: 'stars' })
        if (boroughFilter) params.append('borough', boroughFilter)
        if (cuisineFilter.trim()) params.append('cuisine', cuisineFilter.trim())
        return params
    }

    const formatDate = (value) => {
        if (!value || value === '1900-01-01') {
            return null
        }
        const date = new Date(value)
        if (Number.isNaN(date.getTime())) {
            return null
        }
        return date.toLocaleDateString()
    }

    async function onSearch(e) {
        e.preventDefault()
        const trimmed = query.trim()

        if (!trimmed && !boroughFilter && !cuisineFilter.trim()) {
            setRawResults([])
            setError(null)
            return
        }

        try {
            setLoading(true)
            setError(null)
            const params = buildSearchParams(trimmed)
            const url = `/api/restaurants/search/?${params}`
            const res = await fetch(url)
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}))
                const errorMsg = errorData.detail || errorData.message || `Request failed with status ${res.status}`
                throw new Error(errorMsg)
            }
            
            const data = await res.json()
            const list = Array.isArray(data) ? data : (data.results ?? [])
            setRawResults(list)
            
            if (list.length === 0) {
                setError(null) // Clear error, just show empty state
            }
        } catch (err) {
            console.error('Search error:', err)
            setError(err?.message || 'Failed to search restaurants. Please try again.')
            setRawResults([])
        } finally {
            setLoading(false)
        }
    }

    async function onFilterSearch() {
        if (!boroughFilter && !cuisineFilter.trim() && !query.trim()) {
            setError('Please select at least one filter (borough or cuisine) or enter a restaurant name')
            return
        }

        try {
            setLoading(true)
            setError(null)
            const params = buildSearchParams(query.trim())
            const url = `/api/restaurants/search/?${params}`
            const res = await fetch(url)
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}))
                const errorMsg = errorData.detail || errorData.message || `Request failed with status ${res.status}`
                throw new Error(errorMsg)
            }
            
            const data = await res.json()
            const list = Array.isArray(data) ? data : (data.results ?? [])
            setRawResults(list)
            
            if (list.length === 0) {
                setError(null) // Clear error, just show empty state
            }
        } catch (err) {
            console.error('Filter search error:', err)
            setError(err?.message || 'Failed to search restaurants. Please try again.')
            setRawResults([])
        } finally {
            setLoading(false)
        }
    }

    async function onRestaurantClick(restaurantId) {
        try {
            setDetailLoading(true)
            setError(null)
            const res = await fetch(`/api/restaurants/${restaurantId}/?display=stars`)
            if (!res.ok) throw new Error(`Request failed: ${res.status}`)
            const data = await res.json()
            setSelectedRestaurant(data)
        } catch (err) {
            setError(err?.message || 'Failed to load restaurant details')
        } finally {
            setDetailLoading(false)
        }
    }

    function closeModal() {
        setSelectedRestaurant(null)
    }

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="app-header-content">
                    <button className="logo-button" onClick={() => navigate('/')}>
                        <h1 className="app-logo">SafeEats<span className="logo-nyc">NYC</span></h1>
                    </button>
                    <p className="app-subtitle">Restaurant Safety Ratings</p>
                </div>
            </header>

            <div className="search-section">
                <div className="search-wrapper">
                    <form onSubmit={onSearch} className="search-bar">
                        <div className="search-input-wrapper">
                            <span className="search-icon">🔍</span>
                            <input
                                className="search-input"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Search restaurants by name..."
                                aria-label="Restaurant name"
                            />
                        </div>
                        <button className="search-button" disabled={loading} type="submit">
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </form>
                </div>

                <div className="filters-panel">
                    <div className="filter-row">
                        <div className="filter-item">
                            <label htmlFor="borough-select" className="filter-label">Borough</label>
                            <select
                                id="borough-select"
                                value={boroughFilter}
                                onChange={(e) => {
                                    setBoroughFilter(e.target.value)
                                    if (query.trim()) {
                                        setTimeout(() => onSearch({ preventDefault: () => { } }), 100)
                                    }
                                }}
                                className="filter-select"
                            >
                                <option value="">All Boroughs</option>
                                {boroughs.map(borough => (
                                    <option key={borough} value={borough}>{borough}</option>
                                ))}
                            </select>
                        </div>

                        <div className="filter-item">
                            <label htmlFor="cuisine-input" className="filter-label">Cuisine</label>
                            <input
                                id="cuisine-input"
                                type="text"
                                value={cuisineFilter}
                                onChange={(e) => {
                                    setCuisineFilter(e.target.value)
                                    if (query.trim()) {
                                        setTimeout(() => onSearch({ preventDefault: () => { } }), 300)
                                    }
                                }}
                                placeholder="Italian, Chinese, etc."
                                className="filter-input"
                            />
                        </div>

                        <div className="filter-item">
                            <label htmlFor="sort-select" className="filter-label">Sort</label>
                            <select
                                id="sort-select"
                                value={sortOption}
                                onChange={(e) => setSortOption(e.target.value)}
                                className="filter-select"
                            >
                                <option value="stars_desc">⭐ Highest Rated</option>
                                <option value="stars_asc">⭐ Lowest Rated</option>
                                <option value="name_asc">A–Z</option>
                                <option value="name_desc">Z–A</option>
                            </select>
                        </div>

                        <button
                            type="button"
                            onClick={onFilterSearch}
                            className="filter-search-button"
                            disabled={loading}
                        >
                            Apply Filters
                        </button>
                    </div>
                </div>
            </div>

            <main className="main-content">
                {loading && (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>Searching NYC restaurants...</p>
                    </div>
                )}
                
                {error && (
                    <div className="error-message" role="alert">
                        <span className="error-icon">⚠️</span>
                        <span>{error}</span>
                    </div>
                )}

                {!loading && !error && results.length === 0 && (
                    <div className="empty-state">
                        <img 
                            src={getImagePath("placeholder-nyc-skyline.jpg")} 
                            alt="NYC" 
                            className="empty-image"
                        />
                        <h3>Start Your Search</h3>
                        <p>Enter a restaurant name or use the filters above to find dining spots across NYC.</p>
                    </div>
                )}

                {!loading && !error && results.length > 0 && (
                    <>
                        <div className="results-header">
                            <h2 className="results-title">Found {results.length} restaurant{results.length !== 1 ? 's' : ''}</h2>
                        </div>
                        <div className="results-grid">
                            {results.map((r) => {
                                const latestDate = formatDate(r?.latest_inspection?.date)
                                return (
                                    <div
                                        key={r.id}
                                        className="restaurant-card"
                                        onClick={() => onRestaurantClick(r.id)}
                                        role="button"
                                        tabIndex={0}
                                        onKeyDown={(event) => {
                                            if (event.key === 'Enter' || event.key === ' ') {
                                                event.preventDefault()
                                                onRestaurantClick(r.id)
                                            }
                                        }}
                                    >
                                        <div className="card-content">
                                            <div className="card-header-row">
                                                <h3 className="card-name">{r.name}</h3>
                                                <StarDisplay value={r?.star_rating ?? r?.display_value} />
                                            </div>
                                            {(() => {
                                                const addressText = [r.address, r.city, r.state, r.zipcode].filter(Boolean).join(', ')
                                                const mapsUrl = buildMapsUrl(r.address, r.city, r.state, r.zipcode)
                                                return mapsUrl ? (
                                                    <a 
                                                        href={mapsUrl} 
                                                        target="_blank" 
                                                        rel="noopener noreferrer"
                                                        className="card-address-link"
                                                        onClick={(e) => e.stopPropagation()}
                                                    >
                                                        📍 {addressText}
                                                    </a>
                                                ) : (
                                                    <p className="card-address">
                                                        📍 {addressText}
                                                    </p>
                                                )
                                            })()}
                                            {latestDate && (
                                                <p className="card-date">Last inspected: {latestDate}</p>
                                            )}
                                            {(r.borough || r.cuisine_description) && (
                                                <div className="card-tags">
                                                    {r.borough && <span className="card-tag borough">{r.borough}</span>}
                                                    {r.cuisine_description && <span className="card-tag cuisine">{r.cuisine_description}</span>}
                                                </div>
                                            )}
                                            {r.latest_inspection?.summary && (
                                                <p className="card-summary">
                                                    {r.latest_inspection?.violation_code && (
                                                        <span className="violation-code">{r.latest_inspection.violation_code}: </span>
                                                    )}
                                                    {r.latest_inspection.summary.substring(0, 120)}
                                                    {r.latest_inspection.summary.length > 120 && '...'}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </>
                )}
            </main>

            {selectedRestaurant && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={closeModal} aria-label="Close">×</button>
                        
                        <div className="modal-header">
                            <h2 className="modal-title">{selectedRestaurant.name}</h2>
                            <div className="modal-rating-large">
                                <StarDisplay value={selectedRestaurant?.star_rating ?? selectedRestaurant?.display_value} size="large" />
                                <p className="modal-rating-note">SafeEats Rating (based on 2021–2025 inspections)</p>
                            </div>
                        </div>

                        <div className="modal-body">
                            <div className="modal-info-grid">
                                <div className="modal-info-item">
                                    <span className="info-label">📍 Address</span>
                                    {(() => {
                                        const addressText = [selectedRestaurant.address, selectedRestaurant.city, selectedRestaurant.state, selectedRestaurant.zipcode].filter(Boolean).join(', ')
                                        const mapsUrl = buildMapsUrl(selectedRestaurant.address, selectedRestaurant.city, selectedRestaurant.state, selectedRestaurant.zipcode)
                                        return mapsUrl ? (
                                            <a 
                                                href={mapsUrl} 
                                                target="_blank" 
                                                rel="noopener noreferrer"
                                                className="info-value-link"
                                            >
                                                {addressText}
                                            </a>
                                        ) : (
                                            <span className="info-value">{addressText}</span>
                                        )
                                    })()}
                                </div>
                                {selectedRestaurant.borough && (
                                    <div className="modal-info-item">
                                        <span className="info-label">🗺️ Borough</span>
                                        <span className="info-value">{selectedRestaurant.borough}</span>
                                    </div>
                                )}
                                {selectedRestaurant.cuisine_description && (
                                    <div className="modal-info-item">
                                        <span className="info-label">🍽️ Cuisine</span>
                                        <span className="info-value">{selectedRestaurant.cuisine_description}</span>
                                    </div>
                                )}
                                {selectedRestaurant.phone && (
                                    <div className="modal-info-item">
                                        <span className="info-label">📞 Phone</span>
                                        <span className="info-value">{selectedRestaurant.phone}</span>
                                    </div>
                                )}
                                {selectedRestaurant.camis && (
                                    <div className="modal-info-item">
                                        <span className="info-label">🆔 CAMIS</span>
                                        <span className="info-value code">{selectedRestaurant.camis}</span>
                                    </div>
                                )}
                            </div>

                            <h3 className="inspection-section-title">Inspection History</h3>
                            {detailLoading ? (
                                <div className="loading-state">
                                    <div className="loading-spinner"></div>
                                    <p>Loading inspection history...</p>
                                </div>
                            ) : selectedRestaurant.inspections && selectedRestaurant.inspections.length > 0 ? (
                                <div className="inspection-timeline">
                                    {selectedRestaurant.inspections.map((inspection) => {
                                        const readableDate = formatDate(inspection.date) || 'Date Unknown'
                                        return (
                                            <div key={inspection.id} className="inspection-entry">
                                                <div className="inspection-date-badge">{readableDate}</div>
                                                {inspection.summary && (
                                                    <div className="inspection-details">
                                                        {inspection.violation_code && (
                                                            <span className="violation-code">{inspection.violation_code}: </span>
                                                        )}
                                                        {inspection.summary}
                                                    </div>
                                                )}
                                                {inspection.action && (
                                                    <div className="inspection-action">
                                                        <strong>Action:</strong> {inspection.action}
                                                    </div>
                                                )}
                                                {inspection.critical_flag && (
                                                    <div className="inspection-flag">
                                                        <strong>Critical Flag:</strong> {inspection.critical_flag}
                                                    </div>
                                                )}
                                            </div>
                                        )
                                    })}
                                </div>
                            ) : (
                                <p className="no-inspections">No inspection history available.</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
