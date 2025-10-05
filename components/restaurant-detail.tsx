"use client"

interface Restaurant {
  id: string
  name: string
  borough: string
  cuisine: string
  grade: string
  address: string
  phone: string
  inspectionDate: string
  score: number
  violations: Array<{
    code: string
    description: string
    critical: boolean
  }>
}

interface RestaurantDetailProps {
  restaurant: Restaurant
  onBack: () => void
}

export default function RestaurantDetail({ restaurant, onBack }: RestaurantDetailProps) {
  const getGradeBadgeClass = (grade: string) => {
    switch (grade) {
      case "A":
        return "bg-success"
      case "B":
        return "bg-warning text-dark"
      case "C":
        return "bg-danger"
      default:
        return "bg-secondary"
    }
  }

  const criticalViolations = restaurant.violations.filter((v) => v.critical)
  const nonCriticalViolations = restaurant.violations.filter((v) => !v.critical)

  return (
    <div>
      {/* Back Button */}
      <button className="btn btn-link text-decoration-none ps-0 mb-3" onClick={onBack}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          fill="currentColor"
          className="bi bi-arrow-left me-1"
          viewBox="0 0 16 16"
        >
          <path
            fillRule="evenodd"
            d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"
          />
        </svg>
        Back to results
      </button>

      {/* Restaurant Header */}
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h2 className="card-title mb-2 fw-bold">{restaurant.name}</h2>
              <p className="text-muted mb-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-geo-alt-fill me-2"
                  viewBox="0 0 16 16"
                >
                  <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z" />
                </svg>
                {restaurant.address}
              </p>
              <p className="text-muted mb-0">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-telephone-fill me-2"
                  viewBox="0 0 16 16"
                >
                  <path
                    fillRule="evenodd"
                    d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.678.678 0 0 0 .178.643l2.457 2.457a.678.678 0 0 0 .644.178l2.189-.547a1.745 1.745 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.634 18.634 0 0 1-7.01-4.42 18.634 18.634 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877L1.885.511z"
                  />
                </svg>
                {restaurant.phone}
              </p>
            </div>
            <span className={`badge ${getGradeBadgeClass(restaurant.grade)} display-6 px-4 py-3`}>
              {restaurant.grade}
            </span>
          </div>

          <div className="row g-3">
            <div className="col-md-3">
              <div className="border rounded p-3 text-center">
                <div className="text-muted small mb-1">Borough</div>
                <div className="fw-bold">{restaurant.borough}</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="border rounded p-3 text-center">
                <div className="text-muted small mb-1">Cuisine</div>
                <div className="fw-bold">{restaurant.cuisine}</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="border rounded p-3 text-center">
                <div className="text-muted small mb-1">Inspection Score</div>
                <div className="fw-bold">{restaurant.score}</div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="border rounded p-3 text-center">
                <div className="text-muted small mb-1">Inspection Date</div>
                <div className="fw-bold">{new Date(restaurant.inspectionDate).toLocaleDateString()}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grade Information */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-white">
          <h5 className="mb-0 fw-bold">Understanding Grades</h5>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-4">
              <div className="d-flex align-items-center">
                <span className="badge bg-success fs-5 px-3 py-2 me-3">A</span>
                <div>
                  <div className="fw-semibold">Grade A</div>
                  <small className="text-muted">Score: 0-13 points</small>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center">
                <span className="badge bg-warning text-dark fs-5 px-3 py-2 me-3">B</span>
                <div>
                  <div className="fw-semibold">Grade B</div>
                  <small className="text-muted">Score: 14-27 points</small>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center">
                <span className="badge bg-danger fs-5 px-3 py-2 me-3">C</span>
                <div>
                  <div className="fw-semibold">Grade C</div>
                  <small className="text-muted">Score: 28+ points</small>
                </div>
              </div>
            </div>
          </div>
          <div className="alert alert-info mt-3 mb-0">
            <small>Lower scores indicate better compliance with health and safety regulations.</small>
          </div>
        </div>
      </div>

      {/* Violations */}
      <div className="card shadow-sm">
        <div className="card-header bg-white">
          <h5 className="mb-0 fw-bold">Inspection Violations</h5>
        </div>
        <div className="card-body">
          {restaurant.violations.length === 0 ? (
            <div className="text-center py-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                fill="currentColor"
                className="bi bi-check-circle text-success mb-2"
                viewBox="0 0 16 16"
              >
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z" />
              </svg>
              <p className="text-success fw-semibold mb-0">No violations found</p>
            </div>
          ) : (
            <>
              {criticalViolations.length > 0 && (
                <div className="mb-4">
                  <h6 className="text-danger fw-bold mb-3">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      className="bi bi-exclamation-triangle-fill me-2"
                      viewBox="0 0 16 16"
                    >
                      <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z" />
                    </svg>
                    Critical Violations ({criticalViolations.length})
                  </h6>
                  {criticalViolations.map((violation, index) => (
                    <div key={index} className="alert alert-danger d-flex align-items-start mb-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        fill="currentColor"
                        className="bi bi-x-circle-fill me-3 flex-shrink-0 mt-1"
                        viewBox="0 0 16 16"
                      >
                        <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z" />
                      </svg>
                      <div>
                        <div className="fw-semibold mb-1">Code: {violation.code}</div>
                        <div>{violation.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {nonCriticalViolations.length > 0 && (
                <div>
                  <h6 className="text-warning fw-bold mb-3">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      fill="currentColor"
                      className="bi bi-exclamation-circle-fill me-2"
                      viewBox="0 0 16 16"
                    >
                      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z" />
                    </svg>
                    Non-Critical Violations ({nonCriticalViolations.length})
                  </h6>
                  {nonCriticalViolations.map((violation, index) => (
                    <div key={index} className="alert alert-warning d-flex align-items-start mb-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        fill="currentColor"
                        className="bi bi-info-circle-fill me-3 flex-shrink-0 mt-1"
                        viewBox="0 0 16 16"
                      >
                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z" />
                      </svg>
                      <div>
                        <div className="fw-semibold mb-1">Code: {violation.code}</div>
                        <div>{violation.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
