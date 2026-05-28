import { CloudRain, Thermometer, Wind } from "lucide-react";

function App() {
  const cards = [
    {
      title: "Temperature",
      value: "34°C",
      desc: "Extreme Heat Risk",
      icon: <Thermometer size={40} />,
    },
    {
      title: "Rainfall",
      value: "82%",
      desc: "Flood Warning",
      icon: <CloudRain size={40} />,
    },
    {
      title: "Air Quality",
      value: "151",
      desc: "Moderate Pollution",
      icon: <Wind size={40} />,
    },
  ];

  return (
    <div
      style={{
        background: "#020617",
        minHeight: "100vh",
        color: "white",
        padding: "40px",
        fontFamily: "sans-serif",
      }}
    >
      <h1
        style={{
          fontSize: "70px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        ClimateShield AI
      </h1>

      <p
        style={{
          textAlign: "center",
          color: "#94a3b8",
          fontSize: "22px",
          marginBottom: "60px",
        }}
      >
        AI Climate Intelligence Platform
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))",
          gap: "30px",
        }}
      >
        {cards.map((card, index) => (
          <div
            key={index}
            style={{
              background: "#0f172a",
              borderRadius: "25px",
              padding: "35px",
              border: "1px solid #1e293b",
              boxShadow: "0px 0px 25px rgba(59,130,246,0.15)",
            }}
          >
            <div style={{ color: "#3b82f6" }}>
              {card.icon}
            </div>

            <h2
              style={{
                marginTop: "20px",
                fontSize: "30px",
              }}
            >
              {card.title}
            </h2>

            <h1
              style={{
                fontSize: "65px",
                margin: "20px 0",
              }}
            >
              {card.value}
            </h1>

            <p
              style={{
                color: "#94a3b8",
                fontSize: "20px",
              }}
            >
              {card.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;