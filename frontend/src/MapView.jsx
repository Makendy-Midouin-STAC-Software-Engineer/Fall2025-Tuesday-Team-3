import React, { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in webpack/vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

/**
 * Get color for marker based on grade/rating
 */
const getMarkerColor = (restaurant) => {
    const rating = restaurant?.star_rating ?? restaurant?.display_value ?? 0
    const grade = restaurant?.regraded_letter?.toUpperCase() || ''
    
    // Use star rating if available, otherwise fall back to letter grade
    if (rating >= 4) return '#22c55e' // Green for 4 stars
    if (rating >= 3) return '#84cc16' // Light green for 3 stars
    if (rating >= 2) return '#eab308' // Yellow for 2 stars
    if (rating >= 1) return '#f97316' // Orange for 1 star
    
    // Fall back to letter grades
    if (grade === 'A') return '#22c55e' // Green
    if (grade === 'B') return '#eab308' // Yellow
    if (grade === 'C' || grade === 'D' || grade === 'F') return '#ef4444' // Red
    
    return '#6b7280' // Gray for unknown
}

/**
 * Create custom colored marker
 */
const createCustomMarker = (color) => {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${color};
            width: 20px;
            height: 20px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 20],
    })
}

export default function MapView({ restaurants, onRestaurantClick, selectedRestaurantId }) {
    const mapRef = useRef(null)
    const mapInstanceRef = useRef(null)
    const markersRef = useRef([])

    useEffect(() => {
        // Initialize map
        if (!mapRef.current) return

        if (!mapInstanceRef.current) {
            // Center on NYC (Manhattan)
            const nycCenter = [40.7128, -73.9352]
            
            mapInstanceRef.current = L.map(mapRef.current, {
                center: nycCenter,
                zoom: 11,
                zoomControl: true,
            })

            // Add OpenStreetMap tiles (free, no API key)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19,
            }).addTo(mapInstanceRef.current)
        }

        const map = mapInstanceRef.current

        // Clear existing markers
        markersRef.current.forEach(marker => marker.remove())
        markersRef.current = []

        // Filter restaurants with valid coordinates
        const restaurantsWithCoords = restaurants.filter(
            r => r.latitude != null && r.longitude != null
        )

        if (restaurantsWithCoords.length === 0) {
            return
        }

        // Create markers for each restaurant
        const bounds = []
        restaurantsWithCoords.forEach(restaurant => {
            const lat = parseFloat(restaurant.latitude)
            const lng = parseFloat(restaurant.longitude)
            
            if (isNaN(lat) || isNaN(lng)) return

            const color = getMarkerColor(restaurant)
            const marker = L.marker([lat, lng], {
                icon: createCustomMarker(color),
            })

            // Create popup content
            const popupContent = `
                <div style="min-width: 200px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">
                        ${restaurant.name || 'Unknown'}
                    </h3>
                    <p style="margin: 4px 0; font-size: 12px; color: #666;">
                        ${restaurant.address || ''}${restaurant.city ? `, ${restaurant.city}` : ''}
                    </p>
                    ${restaurant.regraded_letter ? `
                        <p style="margin: 4px 0; font-size: 12px;">
                            <strong>Grade:</strong> ${restaurant.regraded_letter}
                        </p>
                    ` : ''}
                    ${restaurant.star_rating ? `
                        <p style="margin: 4px 0; font-size: 12px;">
                            <strong>Rating:</strong> ${restaurant.star_rating} / 4 ⭐
                        </p>
                    ` : ''}
                    <button 
                        style="
                            margin-top: 8px;
                            padding: 6px 12px;
                            background: #3b82f6;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 12px;
                        "
                        onclick="window.mapRestaurantClick && window.mapRestaurantClick(${restaurant.id})"
                    >
                        View Details
                    </button>
                </div>
            `

            marker.bindPopup(popupContent)
            marker.addTo(map)

            // Handle click
            marker.on('click', () => {
                if (onRestaurantClick) {
                    onRestaurantClick(restaurant.id)
                }
            })

            markersRef.current.push(marker)
            bounds.push([lat, lng])
        })

        // Fit map to show all markers
        if (bounds.length > 0) {
            if (bounds.length === 1) {
                map.setView(bounds[0], 15)
            } else {
                map.fitBounds(bounds, { padding: [50, 50] })
            }
        }

        // Expose click handler globally for popup button
        window.mapRestaurantClick = onRestaurantClick

        // Cleanup
        return () => {
            markersRef.current.forEach(marker => marker.remove())
            markersRef.current = []
        }
    }, [restaurants, onRestaurantClick, selectedRestaurantId])

    return (
        <div 
            ref={mapRef} 
            style={{ 
                width: '100%', 
                height: '500px',
                borderRadius: '8px',
                overflow: 'hidden',
                border: '1px solid #e5e7eb'
            }} 
        />
    )
}

