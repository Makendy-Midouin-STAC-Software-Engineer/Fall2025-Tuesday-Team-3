"use client"

import { useState } from "react"
import SearchBar from "@/components/search-bar"
import FilterPanel from "@/components/filter-panel"
import RestaurantResults from "@/components/restaurant-results"
import RestaurantDetail from "@/components/restaurant-detail"

// Mock data for demonstration
const mockRestaurants = [
  {
    id: "1",
    name: "Joe's Pizza",
    borough: "Manhattan",
    cuisine: "Pizza",
    grade: "A",
    address: "7 Carmine St, New York, NY 10014",
    phone: "(212) 366-1182",
    inspectionDate: "2024-03-15",
    score: 10,
    violations: [
      { code: "04L", description: "Evidence of mice or live mice present", critical: true },
      { code: "10F", description: "Non-food contact surface improperly constructed", critical: false },
    ],
  },
  {
    id: "2",
    name: "Katz's Delicatessen",
    borough: "Manhattan",
    cuisine: "Deli",
    grade: "A",
    address: "205 E Houston St, New York, NY 10002",
    phone: "(212) 254-2246",
    inspectionDate: "2024-02-20",
    score: 8,
    violations: [{ code: "06D", description: "Food contact surface not properly washed", critical: false }],
  },
  {
    id: "3",
    name: "Peter Luger Steak House",
    borough: "Brooklyn",
    cuisine: "Steakhouse",
    grade: "A",
    address: "178 Broadway, Brooklyn, NY 11211",
    phone: "(718) 387-7400",
    inspectionDate: "2024-01-10",
    score: 12,
    violations: [{ code: "02G", description: "Cold food item held above 41°F", critical: true }],
  },
  {
    id: "4",
    name: "Di Fara Pizza",
    borough: "Brooklyn",
    cuisine: "Pizza",
    grade: "B",
    address: "1424 Avenue J, Brooklyn, NY 11230",
    phone: "(718) 258-1367",
    inspectionDate: "2024-03-01",
    score: 18,
    violations: [
      { code: "04L", description: "Evidence of mice or live mice present", critical: true },
      { code: "06C", description: "Food not protected from potential contamination", critical: true },
      { code: "10B", description: "Plumbing not properly installed", critical: false },
    ],
  },
  {
    id: "5",
    name: "Shake Shack",
    borough: "Queens",
    cuisine: "Burgers",
    grade: "A",
    address: "86-02 Queens Blvd, Elmhurst, NY 11373",
    phone: "(929) 244-5858",
    inspectionDate: "2024-02-28",
    score: 9,
    violations: [{ code: "08A", description: "Facility not vermin proof", critical: false }],
  },
]

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("")
  const [filters, setFilters] = useState({
    borough: "",
    cuisine: "",
    grade: "",
  })
  const [selectedRestaurant, setSelectedRestaurant] = useState<(typeof mockRestaurants)[0] | null>(null)

  // Filter restaurants based on search and filters
  const filteredRestaurants = mockRestaurants.filter((restaurant) => {
    const matchesSearch = restaurant.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesBorough = !filters.borough || restaurant.borough === filters.borough
    const matchesCuisine = !filters.cuisine || restaurant.cuisine === filters.cuisine
    const matchesGrade = !filters.grade || restaurant.grade === filters.grade

    return matchesSearch && matchesBorough && matchesCuisine && matchesGrade
  })

  return (
    <>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN"
        crossOrigin="anonymous"
      />

      <div className="min-vh-100 bg-light">
        {/* Header */}
        <header className="bg-primary text-white py-4 shadow-sm">
          <div className="container">
            <h1 className="display-5 fw-bold mb-2">NYC Restaurant Inspector</h1>
            <p className="lead mb-0">Find safe restaurants with verified inspection data</p>
          </div>
        </header>

        {/* Main Content */}
        <main className="container py-4">
          {/* Search Bar */}
          <SearchBar searchQuery={searchQuery} onSearchChange={setSearchQuery} />

          <div className="row g-4 mt-2">
            {/* Filter Panel */}
            <div className="col-lg-3">
              <FilterPanel filters={filters} onFilterChange={setFilters} />
            </div>

            {/* Results or Detail View */}
            <div className="col-lg-9">
              {selectedRestaurant ? (
                <RestaurantDetail restaurant={selectedRestaurant} onBack={() => setSelectedRestaurant(null)} />
              ) : (
                <RestaurantResults restaurants={filteredRestaurants} onSelectRestaurant={setSelectedRestaurant} />
              )}
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-dark text-white py-4 mt-5">
          <div className="container text-center">
            <p className="mb-0">Data sourced from NYC Open Data • Updated regularly</p>
          </div>
        </footer>
      </div>
    </>
  )
}
