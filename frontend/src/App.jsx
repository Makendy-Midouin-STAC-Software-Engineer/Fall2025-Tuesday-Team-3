import React, { useState } from 'react'
import './styles.css'

export default function App() {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function onSearch(e) {
        e.preventDefault()
        const q = query.trim()
        if (!q) {
            setResults([])
            return
        }
        try {
            setLoading(true)
            setError(null)
            const res = await fetch(`/api/restaurants/search/?q=${encodeURIComponent(q)}`)
            if (!res.ok) throw new Error(`Request failed: ${res.status}`)
            const data = await res.json()
            const list = Array.isArray(data) ? data : data.results ?? []
            setResults(list)
        } catch (err) {
            setError(err?.message || 'Unknown error')
            setResults([])
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

            {loading && <p className="muted">Loading...</p>}
            {error && <p role="alert" className="error">{error}</p>}

            {!loading && !error && results.length === 0 && (
                <p className="muted">Try searching for a restaurant name.</p>
            )}

            {!loading && !error && results.length > 0 && (
                <div className="results">
                    {results.map((r) => {
                        const grade = r?.latest_inspection?.grade
                        const badgeClass = grade === 'A' ? 'badge success' : grade ? 'badge warn' : 'badge'
                        return (
                            <div key={r.id} className="card">
                                <div className="card-header">
                                    <span className="name">{r.name}</span>
                                    {grade ? <span className={badgeClass}>Grade: {grade}</span> : <span className="badge">Grade: N/A</span>}
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


