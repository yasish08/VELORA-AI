import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function MapView({ locations }) {
  // Default center
  const center = [0, 0];
  
  if (!locations || locations.length === 0) {
    return <div className="no-data">No location data available</div>;
  }

  return (
    <div className="map-container">
      <h3>Data Locations</h3>
      <MapContainer 
        center={center} 
        zoom={2} 
        style={{ height: '400px', width: '100%', borderRadius: '8px' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {locations.map((loc, index) => (
          <Marker key={index} position={[loc.latitude, loc.longitude]}>
            <Popup>
              {loc.region}<br />
              Temperature: {loc.temperature}°C
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
