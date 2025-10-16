import React, { useState } from 'react'
import './styles.css'

export default function App() {
    const [query, setQuery] = useState('')
    const [rawResults, setRawResults] = useState([])
    const [sortOption, setSortOption] = useState('grade_asc')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [selectedRestaurant, setSelectedRestaurant] = useState(null)
    const [detailLoading, setDetailLoading] = useState(false)
    const [sortBy, setSortBy] = useState('name') // 'name', 'grade', 'score-low', 'score-high'
    const [filters, setFilters] = useState({
        borough: '',
        cuisine: ''
    })

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
        if (!q) {
            setRawResults([])
            return
        }
        try {
            setLoading(true)
            setError(null)
            const res = await fetch(`/api/restaurants/search/?q=${encodeURIComponent(q)}`)
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

    function goBack() {
        setSelectedRestaurant(null)
    }

    // Filter and sort results based on selected criteria
    function filterAndSortResults(results) {
        // First filter by borough and cuisine
        let filteredResults = results.filter(restaurant => {
            const matchesBorough = !filters.borough || 
                restaurant.address?.toLowerCase().includes(filters.borough.toLowerCase()) ||
                restaurant.city?.toLowerCase().includes(filters.borough.toLowerCase())
            
            const matchesCuisine = !filters.cuisine || 
                restaurant.name?.toLowerCase().includes(filters.cuisine.toLowerCase())
            
            return matchesBorough && matchesCuisine
        })

        // Then sort the filtered results
        return filteredResults.sort((a, b) => {
            switch (sortBy) {
                case 'grade':
                    // Sort by grade: A > B > C > N/A
                    const gradeOrder = { 'A': 1, 'B': 2, 'C': 3, '': 4 }
                    const gradeA = a?.latest_inspection?.grade || ''
                    const gradeB = b?.latest_inspection?.grade || ''
                    return gradeOrder[gradeA] - gradeOrder[gradeB]
                
                case 'score-low':
                    // Sort by score: lowest to highest
                    const scoreA = a?.latest_inspection?.score || 999
                    const scoreB = b?.latest_inspection?.score || 999
                    return scoreA - scoreB
                
                case 'score-high':
                    // Sort by score: highest to lowest
                    const scoreHighA = a?.latest_inspection?.score || -1
                    const scoreHighB = b?.latest_inspection?.score || -1
                    return scoreHighB - scoreHighA
                
                case 'name':
                default:
                    // Sort by name alphabetically
                    return a.name.localeCompare(b.name)
            }
        })
    }

    // If we have a selected restaurant, show the detail view
    if (selectedRestaurant) {
        return (
            <div className="container">
                <div className="header">
                    <button className="back-button" onClick={goBack}>← Back to Search</button>
                    <div className="title">Restaurant Details</div>
                </div>

                {detailLoading && <p className="muted">Loading restaurant details...</p>}
                {error && <p role="alert" className="error">{error}</p>}

                {!detailLoading && !error && selectedRestaurant && (
                    <div className="restaurant-detail">
                        <div className="detail-header">
                            <h2 className="restaurant-name">{selectedRestaurant.name}</h2>
                            <div className="restaurant-address">{selectedRestaurant.full_address}</div>
                            {selectedRestaurant.camis && (
                                <div className="camis">CAMIS ID: {selectedRestaurant.camis}</div>
                            )}
                        </div>

                        {selectedRestaurant.latest_inspection && (
                            <div className="current-grade">
                                <h3>Current Grade</h3>
                                <div className={`grade-display ${selectedRestaurant.latest_inspection.grade?.toLowerCase() || 'no-grade'}`}>
                                    <span className="grade-letter">{selectedRestaurant.latest_inspection.grade || 'N/A'}</span>
                                    {selectedRestaurant.latest_inspection.score && (
                                        <span className="grade-score">Score: {selectedRestaurant.latest_inspection.score}</span>
                                    )}
                                </div>
                                <div className="inspection-date">
                                    Inspection Date: {new Date(selectedRestaurant.latest_inspection.date).toLocaleDateString()}
                                </div>
                            </div>
                        )}

                        <div className="inspections-section">
                            <h3>All Inspections ({selectedRestaurant.total_inspections})</h3>
                            {selectedRestaurant.inspections.length === 0 ? (
                                <p className="muted">No inspection data available</p>
                            ) : (
                                <div className="inspections-list">
                                    {selectedRestaurant.inspections.map((inspection, index) => (
                                        <div key={inspection.id} className={`inspection-card ${index === 0 ? 'latest' : ''}`}>
                                            <div className="inspection-header">
                                                <span className="inspection-date">
                                                    {new Date(inspection.date).toLocaleDateString()}
                                                </span>
                                                <span className={`inspection-grade ${inspection.grade?.toLowerCase() || 'no-grade'}`}>
                                                    Grade: {inspection.grade || 'N/A'}
                                                </span>
                                                {inspection.score && (
                                                    <span className="inspection-score">
                                                        Score: {inspection.score}
                                                    </span>
                                                )}
                                            </div>
                                            {inspection.summary && (
                                                <div className="inspection-summary">{inspection.summary}</div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        )
    }

    // Otherwise, show the search interface
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

            {results.length > 0 && (
                <div className="sort-controls">
                    <label htmlFor="sort-select" className="sort-label">Sort by:</label>
                    <select
                        id="sort-select"
                        value={sortOption}
                        onChange={(e) => setSortOption(e.target.value)}
                        className="sort-select"
                    >
                        <option value="grade_asc">Grade (A → C) - Safest First</option>
                        <option value="grade_desc">Grade (C → A) - Worst First</option>
                        <option value="score_asc">Score (Low → High) - Safest First</option>
                        <option value="score_desc">Score (High → Low) - Worst First</option>
                        <option value="name_asc">Name (A-Z)</option>
                        <option value="name_desc">Name (Z-A)</option>
                    </select>
                </div>
            )}

            {loading && <p className="muted">Loading...</p>}
            {error && <p role="alert" className="error">{error}</p>}

            {!loading && !error && results.length === 0 && (
                <p className="muted">Try searching for a restaurant name.</p>
            )}

            {!loading && !error && results.length > 0 && (
                <div>
                    <div className="filter-controls">
                        <div className="filter-group">
                            <label htmlFor="borough-filter">Borough:</label>
                            <input
                                id="borough-filter"
                                type="text"
                                className="filter-input"
                                placeholder="e.g., Manhattan, Brooklyn"
                                value={filters.borough}
                                onChange={(e) => setFilters(prev => ({ ...prev, borough: e.target.value }))}
                            />
                        </div>
                        <div className="filter-group">
                            <label htmlFor="cuisine-filter">Cuisine:</label>
                            <input
                                id="cuisine-filter"
                                type="text"
                                className="filter-input"
                                placeholder="e.g., Pizza, Italian"
                                value={filters.cuisine}
                                onChange={(e) => setFilters(prev => ({ ...prev, cuisine: e.target.value }))}
                            />
                        </div>
                        <div className="filter-group">
                            <label htmlFor="sort-select">Sort by:</label>
                            <select 
                                id="sort-select"
                                className="sort-select"
                                value={sortBy} 
                                onChange={(e) => setSortBy(e.target.value)}
                            >
                                <option value="name">Name (A-Z)</option>
                                <option value="grade">Grade (A to C)</option>
                                <option value="score-low">Score (Low to High)</option>
                                <option value="score-high">Score (High to Low)</option>
                            </select>
                        </div>
                    </div>
                    
                    <div className="results">
                        {filterAndSortResults(results).map((r) => {
                        const grade = r?.latest_inspection?.grade
                        const score = r?.latest_inspection?.score
                        const badgeClass = grade === 'A' ? 'badge success' : grade ? 'badge warn' : 'badge'
                        return (
                            <div key={r.id} className="card clickable" onClick={() => onRestaurantClick(r.id)}>
                                <div className="card-header">
                                    <span className="name">{r.name}</span>
                                    <div className="badges">
                                        {grade ? <span className={badgeClass}>Grade: {grade}</span> : <span className="badge">Grade: N/A</span>}
                                        {score !== null && score !== undefined && <span className="badge">Score: {score}</span>}
                                    </div>
                                </div>
                                <div className="address">{[r.address, r.city, r.state, r.zipcode].filter(Boolean).join(', ')}</div>
                                {r.latest_inspection?.score && (
                                    <div className="score-display">Inspection Score: {r.latest_inspection.score}</div>
                                )}
                                {r.latest_inspection?.summary && (
                                    <div className="summary">{r.latest_inspection.summary}</div>
                                )}
                                <div className="click-hint">Click to view details</div>
                            </div>
                        )
                    })}
                    </div>
                </div>
            )}
        </div>
    )
}


