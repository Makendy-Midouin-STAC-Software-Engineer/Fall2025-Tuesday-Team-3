import React, { useState } from 'react'
import './styles.css'

export default function App() {
    const [query, setQuery] = useState('')
    const [rawResults, setRawResults] = useState([])
    const [sortOption, setSortOption] = useState('grade_asc')
    const [boroughFilter, setBoroughFilter] = useState('')
    const [cuisineFilter, setCuisineFilter] = useState('')
    const [boroughs, setBoroughs] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [selectedRestaurant, setSelectedRestaurant] = useState(null)
    const [detailLoading, setDetailLoading] = useState(false)

    // Fetch boroughs on component mount
    React.useEffect(() => {
        async function fetchBoroughs() {
            try {
                const res = await fetch('/api/restaurants/boroughs/')
                if (res.ok) {
                    const data = await res.json()
                    setBoroughs(data)
                }
            } catch (err) {
                console.error('Failed to fetch boroughs:', err)
            }
        }
        fetchBoroughs()
    }, [])

    // Client-side sorting function
    const sortResults = (results, sortOption) => {
        return [...results].sort((a, b) => {
            const aGrade = a?.latest_inspection?.grade || ''
            const bGrade = b?.latest_inspection?.grade || ''
            const aScore = a?.latest_inspection?.score ?? 999
            const bScore = b?.latest_inspection?.score ?? 999
            const aName = a?.name || ''
            const bName = b?.name || ''

            switch (sortOption) {
                case 'grade_asc':
                    // A grades first (best), then B, then C, then ungraded last
                    const gradeOrder = { 'A': 1, 'B': 2, 'C': 3 }
                    const aOrder = gradeOrder[aGrade] || 4
                    const bOrder = gradeOrder[bGrade] || 4
                    if (aOrder !== bOrder) return aOrder - bOrder
                    return aName.localeCompare(bName)

                case 'grade_desc':
                    // C grades first (worst), then B, then A, then ungraded last
                    const gradeOrderDesc = { 'C': 1, 'B': 2, 'A': 3 }
                    const aOrderDesc = gradeOrderDesc[aGrade] || 4
                    const bOrderDesc = gradeOrderDesc[bGrade] || 4
                    if (aOrderDesc !== bOrderDesc) return aOrderDesc - bOrderDesc
                    return aName.localeCompare(bName)

                case 'score_asc':
                    // Lowest scores first (safest restaurants)
                    if (aScore !== bScore) return aScore - bScore
                    return aName.localeCompare(bName)

                case 'score_desc':
                    // Highest scores first (least safe restaurants)
                    if (aScore !== bScore) return bScore - aScore
                    return aName.localeCompare(bName)

                case 'name_desc':
                    return bName.localeCompare(aName)

                default: // name_asc
                    return aName.localeCompare(bName)
            }
        })
    }

    // Compute sorted results - only re-sorts when rawResults or sortOption changes
    const results = React.useMemo(() => {
        return sortResults(rawResults, sortOption)
    }, [rawResults, sortOption])

    async function onSearch(e) {
        e.preventDefault()
        const q = query.trim()

        if (!q && !boroughFilter && !cuisineFilter.trim()) {
            setRawResults([])
            return
        }
        try {
            setLoading(true)
            setError(null)

            // Build query parameters - use wildcard if no name but filters exist
            const params = new URLSearchParams({ q: q || '*' })
            if (boroughFilter) params.append('borough', boroughFilter)
            if (cuisineFilter.trim()) params.append('cuisine', cuisineFilter.trim())

            console.log('Search URL:', `/api/restaurants/search/?${params}`)

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
        // Search by filters only (no name required)
        if (!boroughFilter && !cuisineFilter.trim()) {
            setError('Please select at least one filter (borough or cuisine)')
            return
        }

        try {
            setLoading(true)
            setError(null)

            // Build query parameters - use a wildcard search if no name provided
            const params = new URLSearchParams({ q: query.trim() || '*' })
            if (boroughFilter) params.append('borough', boroughFilter)
            if (cuisineFilter.trim()) params.append('cuisine', cuisineFilter.trim())

            console.log('Filter search URL:', `/api/restaurants/search/?${params}`)

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
            const res = await fetch(`/api/restaurants/${restaurantId}/`)
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
            <div className="header">
                <div className="title">SafeEatsNYC</div>
            </div>
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
                        onChange={(e) => setBoroughFilter(e.target.value)}
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
                        onChange={(e) => setCuisineFilter(e.target.value)}
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
                        <option value="grade_asc">Grade (A → C) - Best First</option>
                        <option value="grade_desc">Grade (C → A) - Worst First</option>
                        <option value="score_asc">Score (Low → High) - Fewest Violations First</option>
                        <option value="score_desc">Score (High → Low) - Most Violations First</option>
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
                        const grade = r?.latest_inspection?.grade
                        const score = r?.latest_inspection?.score
                        const badgeClass = grade === 'A' ? 'badge success' : grade ? 'badge warn' : 'badge'
                        return (
                            <div key={r.id} className="card" onClick={() => onRestaurantClick(r.id)} style={{ cursor: 'pointer' }}>
                                <div className="card-header">
                                    <span className="name">{r.name}</span>
                                    <div className="badges">
                                        {r.latest_inspection?.grade ? (
                                            <span className={badgeClass}>Grade: {r.latest_inspection.grade}</span>
                                        ) : r.latest_inspection?.date ? (
                                            <span className="badge">Grade: Pending</span>
                                        ) : (
                                            <span className="badge">No Recent Inspection</span>
                                        )}
                                        {r.latest_inspection?.score !== null && r.latest_inspection?.score !== undefined && (
                                            <span className="badge">Score: {r.latest_inspection.score}</span>
                                        )}
                                    </div>
                                </div>
                                <div className="address">{[r.address, r.city, r.state, r.zipcode].filter(Boolean).join(', ')}</div>
                                {(r.borough || r.cuisine_description) && (
                                    <div className="restaurant-details">
                                        {r.borough && <span className="detail-badge">📍 {r.borough}</span>}
                                        {r.cuisine_description && <span className="detail-badge">🍽️ {r.cuisine_description}</span>}
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
                        <p className="modal-address">
                            {[selectedRestaurant.address, selectedRestaurant.city, selectedRestaurant.state, selectedRestaurant.zipcode].filter(Boolean).join(', ')}
                        </p>
                        {selectedRestaurant.borough && (
                            <p className="modal-borough">📍 {selectedRestaurant.borough}</p>
                        )}
                        {selectedRestaurant.cuisine_description && (
                            <p className="modal-cuisine">🍽️ {selectedRestaurant.cuisine_description}</p>
                        )}
                        {selectedRestaurant.camis && (
                            <p className="modal-camis">CAMIS ID: {selectedRestaurant.camis}</p>
                        )}

                        <h3 className="inspection-history-title">Inspection History</h3>
                        {detailLoading ? (
                            <p className="muted">Loading inspection history...</p>
                        ) : selectedRestaurant.inspections && selectedRestaurant.inspections.length > 0 ? (
                            <div className="inspection-list">
                                {selectedRestaurant.inspections.map((inspection) => {
                                    const gradeClass = inspection.grade === 'A' ? 'badge success' : inspection.grade ? 'badge warn' : 'badge'
                                    const isValidDate = inspection.date && inspection.date !== '1900-01-01'
                                    return (
                                        <div key={inspection.id} className="inspection-item">
                                            <div className="inspection-header">
                                                <span className="inspection-date">
                                                    {isValidDate ? new Date(inspection.date).toLocaleDateString() : 'Date Unknown'}
                                                </span>
                                                <div className="badges">
                                                    {inspection.grade ? (
                                                        <span className={gradeClass}>Grade: {inspection.grade}</span>
                                                    ) : (
                                                        <span className="badge">Grade: Pending</span>
                                                    )}
                                                    {inspection.score !== null && inspection.score !== undefined && (
                                                        <span className="badge">Score: {inspection.score}</span>
                                                    )}
                                                </div>
                                            </div>
                                            {inspection.summary && (
                                                <p className="inspection-summary">
                                                    {inspection.violation_code && (
                                                        <span className="violation-code">{inspection.violation_code}: </span>
                                                    )}
                                                    {inspection.summary}
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


