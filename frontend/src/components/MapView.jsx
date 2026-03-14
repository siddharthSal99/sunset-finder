import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";
import "leaflet/dist/leaflet.css";

const userIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const spotIcon = new L.DivIcon({
  html: `<div style="
    background: linear-gradient(135deg, #f97316, #ea580c);
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid white; box-shadow: 0 1px 4px rgba(0,0,0,0.4);
  "></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
  className: "",
});

const elevationIcon = new L.DivIcon({
  html: `<div style="
    background: linear-gradient(135deg, #2dd4bf, #0d9488);
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid white; box-shadow: 0 1px 4px rgba(0,0,0,0.4);
  "></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
  className: "",
});

function ClickHandler({ onClick }) {
  useMapEvents({ click: (e) => onClick(e.latlng) });
  return null;
}

function FlyTo({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.flyTo(center, map.getZoom(), { duration: 1 });
  }, [center, map]);
  return null;
}

export default function MapView({ position, spots, onMapClick, flyTo }) {
  const center = position || [37.77, -122.42];

  return (
    <MapContainer center={center} zoom={11} className="h-full w-full">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler onClick={onMapClick} />
      {flyTo && <FlyTo center={flyTo} />}

      {position && (
        <Marker position={position} icon={userIcon}>
          <Popup>Selected location</Popup>
        </Marker>
      )}

      {spots.map((spot, i) => (
        <Marker
          key={i}
          position={[spot.lat, spot.lon]}
          icon={spot.spot_type === "elevation" ? elevationIcon : spotIcon}
        >
          <Popup>
            <div className="text-sm space-y-1">
              <p className="font-semibold">
                {spot.spot_type === "elevation" ? "Viewpoint" : "Spot"} #{i + 1}
              </p>
              <p className="text-gray-500">{spot.distance_km} km away</p>
              {spot.spot_type === "elevation" ? (
                <>
                  <p>{spot.elevation_m?.toLocaleString()}m elevation</p>
                  <p className="text-gray-500">Direction: {spot.direction}</p>
                </>
              ) : (
                (spot.conditions || []).map((c) => (
                  <p key={c.field}>
                    {c.field}: {c.value}% ({c.rating})
                  </p>
                ))
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
