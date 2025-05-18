import { useEffect, useState } from 'react';

export default function App() {
  const [clientes, setClientes] = useState([]);

  useEffect(() => {
    fetch("http://20.127.192.215:8000/clientes")
      .then(res => res.json())
      .then(data => setClientes(data))
      .catch(err => console.error("Error al conectar con FastAPI:", err));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clientes registrados:</h1>
      <ul className="list-disc list-inside">
        {clientes.map((cliente) => (
          <li key={cliente.id}>{cliente.nombre} - {cliente.email}</li>
        ))}
      </ul>
    </div>
  );
}
