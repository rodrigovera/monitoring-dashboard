import { useEffect, useState } from "react";

export default function App() {
  const [clientes, setClientes] = useState([]);
  const [form, setForm] = useState({ nombre: "", email: "", api_url: "" });

  useEffect(() => {
    fetch("http://20.127.192.215:8000/clientes")
      .then((res) => res.json())
      .then((data) => setClientes(data));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://20.127.192.215:8000/clientes/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    const data = await res.json();
    alert(data.message);

    // Refrescar lista de clientes
    const updated = await fetch("http://20.127.192.215:8000/clientes");
    setClientes(await updated.json());
    setForm({ nombre: "", email: "", api_url: "" }); // limpiar formulario
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clientes registrados:</h1>
      <ul className="list-disc list-inside mb-6">
        {clientes.map((cliente) => (
          <li key={cliente.id}>
            {cliente.nombre} - {cliente.email}
          </li>
        ))}
      </ul>

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
    </div>
  );
}
