import React, { useState } from 'react'
import './styles.css'

export default function App() {
    const [query, setQuery] = useState('')
    const [rawResults, setRawResults] = useState([])
    const [sortOption, setSortOption] = useState('grade_asc')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

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
                <div className="results">
                    {results.map((r) => {
                        const grade = r?.latest_inspection?.grade
                        const score = r?.latest_inspection?.score
                        const badgeClass = grade === 'A' ? 'badge success' : grade ? 'badge warn' : 'badge'
                        return (
                            <div key={r.id} className="card">
                                <div className="card-header">
                                    <span className="name">{r.name}</span>
                                    <div className="badges">
                                        {grade ? <span className={badgeClass}>Grade: {grade}</span> : <span className="badge">Grade: N/A</span>}
                                        {score !== null && score !== undefined && <span className="badge">Score: {score}</span>}
                                    </div>
                                </div>
                                <div className="address">{[r.address, r.city, r.state, r.zipcode].filter(Boolean).join(', ')}</div>
                                {r.latest_inspection?.summary && (
                                    <div className="summary">{r.latest_inspection.summary}</div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}


