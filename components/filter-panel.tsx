"use client"

interface FilterPanelProps {
  filters: {
    borough: string
    cuisine: string
    grade: string
  }
  onFilterChange: (filters: { borough: string; cuisine: string; grade: string }) => void
}

const boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
const cuisines = ["Pizza", "Deli", "Steakhouse", "Burgers", "Chinese", "Italian", "Mexican", "Japanese"]
const grades = ["A", "B", "C"]

export default function FilterPanel({ filters, onFilterChange }: FilterPanelProps) {
  const handleFilterChange = (filterType: "borough" | "cuisine" | "grade", value: string) => {
    onFilterChange({
      ...filters,
      [filterType]: value,
    })
  }

  const clearFilters = () => {
    onFilterChange({ borough: "", cuisine: "", grade: "" })
  }

  const hasActiveFilters = filters.borough || filters.cuisine || filters.grade

  return (
    <div className="card shadow-sm sticky-top" style={{ top: "1rem" }}>
      <div className="card-header bg-white border-bottom">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0 fw-bold">Filters</h5>
          {hasActiveFilters && (
            <button className="btn btn-sm btn-link text-decoration-none p-0" onClick={clearFilters}>
              Clear all
            </button>
          )}
        </div>
      </div>
      <div className="card-body">
        {/* Borough Filter */}
        <div className="mb-4">
          <label className="form-label fw-semibold text-secondary small text-uppercase">Borough</label>
          <select
            className="form-select"
            value={filters.borough}
            onChange={(e) => handleFilterChange("borough", e.target.value)}
          >
            <option value="">All Boroughs</option>
            {boroughs.map((borough) => (
              <option key={borough} value={borough}>
                {borough}
              </option>
            ))}
          </select>
        </div>

        {/* Cuisine Filter */}
        <div className="mb-4">
          <label className="form-label fw-semibold text-secondary small text-uppercase">Cuisine</label>
          <select
            className="form-select"
            value={filters.cuisine}
            onChange={(e) => handleFilterChange("cuisine", e.target.value)}
          >
            <option value="">All Cuisines</option>
            {cuisines.map((cuisine) => (
              <option key={cuisine} value={cuisine}>
                {cuisine}
              </option>
            ))}
          </select>
        </div>

        {/* Grade Filter */}
        <div className="mb-0">
          <label className="form-label fw-semibold text-secondary small text-uppercase">Inspection Grade</label>
          <div className="d-flex gap-2">
            {grades.map((grade) => (
              <button
                key={grade}
                className={`btn flex-fill ${
                  filters.grade === grade
                    ? grade === "A"
                      ? "btn-success"
                      : grade === "B"
                        ? "btn-warning"
                        : "btn-danger"
                    : "btn-outline-secondary"
                }`}
                onClick={() => handleFilterChange("grade", filters.grade === grade ? "" : grade)}
              >
                {grade}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
