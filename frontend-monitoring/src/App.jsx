import { useEffect, useState } from 'react';

export default function App() {
  const [clientes, setClientes] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://20.127.192.215:8000/clientes")
      .then(res => {
        if (!res.ok) throw new Error("Respuesta no válida del backend");
        return res.json();
      })
      .then(data => setClientes(data))
      .catch(err => {
        console.error("Error al conectar con FastAPI:", err);
        setError(err.message);
      });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clientes registrados:</h1>
      {error && <p className="text-red-600">Error: {error}</p>}
      <ul className="list-disc list-inside">
        {clientes.map((cliente) => (
          <li key={cliente.id}>
            {cliente.nombre} - {cliente.email}
          </li>
        ))}
      </ul>
    </div>
  );
}
