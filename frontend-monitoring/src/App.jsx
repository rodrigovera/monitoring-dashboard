import { useEffect, useState } from "react";

export default function App() {
  const [clientes, setClientes] = useState([]);
  const [form, setForm] = useState({ nombre: "", email: "", api_url: "" });
  const [metricas, setMetricas] = useState({});
  const [clienteActivo, setClienteActivo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://20.55.80.149:8000/clientes")
      .then((res) => res.json())
      .then((data) => setClientes(data));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://20.55.80.149:8000/clientes/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    alert(data.message);
    const updated = await fetch("http://20.55.80.149:8000/clientes");
    setClientes(await updated.json());
    setForm({ nombre: "", email: "", api_url: "" });
  };

  const obtenerMetricas = async (id) => {
    setError(null);
    setMetricas({});
    try {
      const cliente = clientes.find((c) => c.id === id);
      setClienteActivo(cliente);
      const res = await fetch(`http://20.55.80.149:8000/clientes/${id}/metrics`);
      if (!res.ok) throw new Error("No se pudieron obtener las métricas");
      const data = await res.json();
      setMetricas({ [id]: data });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clientes registrados:</h1>
      <ul className="space-y-4 mb-6">
        {clientes.map((cliente) => (
          <li key={cliente.id} className="border p-4 rounded">
            <p className="font-semibold">{cliente.nombre} - {cliente.email}</p>
            <button
              onClick={() => obtenerMetricas(cliente.id)}
              className="mt-2 text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
            >
              Ver métricas
            </button>
            {metricas[cliente.id] && (
              <div className="mt-2 text-sm">
                <p>🧠 CPU: {metricas[cliente.id].cpu_percent}%</p>
                <p>💾 RAM: {metricas[cliente.id].memory_percent}%</p>
                <p>📀 Disco: {metricas[cliente.id].disk_usage}%</p>
              </div>
            )}
          </li>
        ))}
      </ul>

      <h2 className="text-xl font-bold mb-2">Registrar nuevo cliente:</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="nombre"
          placeholder="Nombre"
          value={form.nombre}
          onChange={handleChange}
          className="border p-2 w-full"
          required
        />
        <input
          type="email"
          name="email"
          placeholder="Correo"
          value={form.email}
          onChange={handleChange}
          className="border p-2 w-full"
          required
        />
        <input
          type="text"
          name="api_url"
          placeholder="API URL"
          value={form.api_url}
          onChange={handleChange}
          className="border p-2 w-full"
          required
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Registrar cliente
        </button>
      </form>

      {error && <p className="text-red-500 mt-4">Error: {error}</p>}

      {clienteActivo && (
        <div className="mt-8">
          <h3 className="text-md font-semibold mb-2">Dashboard en tiempo real:</h3>
          <iframe
            src={`http://20.55.80.149:3000/d/fastapi-dashboard-v2/estado-del-sistema-fastapi?orgId=1&var-cliente=${clienteActivo.id}&refresh=10s`}
            width="100%"
            height="400"
            frameBorder="0"
            className="rounded border"
          />
        </div>
      )}
    </div>
  );
}

