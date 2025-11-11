import React, { useMemo, useState } from 'react'
import './styles.css'

const MAX_STARS = 4

const normalizeStarValue = (value) => {
    const numeric = Number(value)
    if (!Number.isFinite(numeric)) {
        return 0
    }
    return Math.max(0, Math.min(MAX_STARS, Math.round(numeric)))
}

const StarDisplay = ({ value }) => {
    const rating = normalizeStarValue(value)
    if (!rating) {
        return <span className="stars-label muted">No star rating yet</span>
    }

    return (
        <div className="stars-rating" aria-label={`${rating} out of ${MAX_STARS} stars`}>
            {[...Array(MAX_STARS)].map((_, index) => (
                <span
                    key={index}
                    className={index < rating ? 'star filled' : 'star'}
                    aria-hidden="true"
                >
                    ★
                </span>
            ))}
            <span className="stars-label">{rating} / {MAX_STARS}</span>
        </div>
    )
}

export default function App() {
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
            return
        }

        try {
            setLoading(true)
            setError(null)
            const params = buildSearchParams(trimmed)
            const res = await fetch(`/api/restaurants/search/?${params}`)
            if (!res.ok) throw new Error(`Request failed: ${res.status}`)
            const data = await res.json()
            const list = Array.isArray(data) ? data : data.results ?? []
            setRawResults(list)
        } catch (err) {
            setError(err?.message || 'Unknown error')
            setRawResults([])
        } finally {
            setLoading(false)
        }
    }

    async function onFilterSearch() {
        if (!boroughFilter && !cuisineFilter.trim() && !query.trim()) {
            setError('Please select at least one filter (borough or cuisine)')
            return
        }

        try {
            setLoading(true)
            setError(null)
            const params = buildSearchParams(query.trim())
            const res = await fetch(`/api/restaurants/search/?${params}`)
            if (!res.ok) throw new Error(`Request failed: ${res.status}`)
            const data = await res.json()
            const list = Array.isArray(data) ? data : data.results ?? []
            setRawResults(list)
        } catch (err) {
            setError(err?.message || 'Unknown error')
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
        <div className="container">
            <header className="header">
                <h1 className="title">SafeEatsNYC</h1>
            </header>
            <p className="subtitle">Search NYC restaurant inspection results</p>

            <form onSubmit={onSearch} className="search-bar">
                <input
                    className="input"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter restaurant name..."
                    aria-label="Restaurant name"
                />
                <button className="button" disabled={loading} type="submit">Search</button>
            </form>

            <div className="filter-controls">
                <div className="filter-group">
                    <label htmlFor="borough-select" className="filter-label">Borough:</label>
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

                <div className="filter-group">
                    <label htmlFor="cuisine-input" className="filter-label">Cuisine:</label>
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
                        placeholder="e.g., Italian, Chinese..."
                        className="filter-input"
                    />
                </div>

                <div className="filter-group">
                    <label htmlFor="sort-select" className="filter-label">Sort by:</label>
                    <select
                        id="sort-select"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                        className="filter-select"
                    >
                        <option value="stars_desc">Star Rating (High → Low)</option>
                        <option value="stars_asc">Star Rating (Low → High)</option>
                        <option value="name_asc">Name (A-Z)</option>
                        <option value="name_desc">Name (Z-A)</option>
                    </select>
                </div>

                <button
                    type="button"
                    onClick={onFilterSearch}
                    className="filter-button"
                    disabled={loading}
                >
                    Search by Filters
                </button>
            </div>

            {loading && <p className="muted">Loading...</p>}
            {error && <p role="alert" className="error">{error}</p>}

            {!loading && !error && results.length === 0 && (
                <p className="muted">Try searching for a restaurant name.</p>
            )}

            {!loading && !error && results.length > 0 && (
                <div className="results">
                    {results.map((r) => {
                        const latestDate = formatDate(r?.latest_inspection?.date)
                        return (
                            <div
                                key={r.id}
                                className="card"
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
                                <div className="card-header">
                                    <span className="name">{r.name}</span>
                                    <StarDisplay value={r?.star_rating ?? r?.display_value} />
                                </div>
                                <div className="address">{[r.address, r.city, r.state, r.zipcode].filter(Boolean).join(', ')}</div>
                                {(latestDate || r.display_mode === 'stars') && (
                                    <div className="card-meta">
                                        {latestDate && <span className="card-pill">Latest inspection: {latestDate}</span>}
                                        <span className="card-pill accent">SafeEats Star Rating</span>
                                    </div>
                                )}
                                {(r.borough || r.cuisine_description) && (
                                    <div className="restaurant-details">
                                        {r.borough && <span className="detail-badge">{r.borough}</span>}
                                        {r.cuisine_description && <span className="detail-badge">{r.cuisine_description}</span>}
                                    </div>
                                )}
                                {r.latest_inspection?.summary && (
                                    <div className="summary">
                                        {r.latest_inspection?.violation_code && (
                                            <span className="violation-code">{r.latest_inspection.violation_code}: </span>
                                        )}
                                        {r.latest_inspection.summary}
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}

            {selectedRestaurant && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={closeModal}>&times;</button>
                        <h2>{selectedRestaurant.name}</h2>
                        <div className="modal-rating">
                            <StarDisplay value={selectedRestaurant?.star_rating ?? selectedRestaurant?.display_value} />
                            <p className="modal-rating-caption">Deterministic star rating (4 = clean since 2021)</p>
                        </div>
                        <p className="modal-address">
                            {[selectedRestaurant.address, selectedRestaurant.city, selectedRestaurant.state, selectedRestaurant.zipcode].filter(Boolean).join(', ')}
                        </p>
                        {selectedRestaurant.borough && (
                            <p className="modal-borough"><strong>Borough:</strong> {selectedRestaurant.borough}</p>
                        )}
                        {selectedRestaurant.cuisine_description && (
                            <p className="modal-cuisine"><strong>Cuisine:</strong> {selectedRestaurant.cuisine_description}</p>
                        )}
                        {selectedRestaurant.camis && (
                            <p className="modal-camis">CAMIS ID: {selectedRestaurant.camis}</p>
                        )}
                        {selectedRestaurant.phone && (
                            <p className="modal-phone"><strong>Phone:</strong> {selectedRestaurant.phone}</p>
                        )}

                        <h3 className="inspection-history-title">Inspection History</h3>
                        {detailLoading ? (
                            <p className="muted">Loading inspection history...</p>
                        ) : selectedRestaurant.inspections && selectedRestaurant.inspections.length > 0 ? (
                            <div className="inspection-list">
                                {selectedRestaurant.inspections.map((inspection) => {
                                    const readableDate = formatDate(inspection.date) || 'Date Unknown'
                                    return (
                                        <div key={inspection.id} className="inspection-item">
                                            <div className="inspection-header">
                                                <span className="inspection-date">{readableDate}</span>
                                            </div>
                                            {inspection.summary && (
                                                <p className="inspection-summary">
                                                    {inspection.violation_code && (
                                                        <span className="violation-code">{inspection.violation_code}: </span>
                                                    )}
                                                    {inspection.summary}
                                                </p>
                                            )}
                                            {inspection.action && (
                                                <p className="inspection-action">
                                                    <strong>Action:</strong> {inspection.action}
                                                </p>
                                            )}
                                            {inspection.critical_flag && (
                                                <p className="inspection-critical-flag">
                                                    <strong>Critical Flag:</strong> {inspection.critical_flag}
                                                </p>
                                            )}
                                        </div>
                                    )
                                })}
                            </div>
                        ) : (
                            <p className="muted">No inspection history available.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
