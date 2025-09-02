const form = document.getElementById("customerForm");
const list = document.getElementById("customerList");
const resetBtn = document.getElementById("resetBtn");

async function loadCustomers() {
    const res = await fetch("/api/customers");
    const data = await res.json();

    list.innerHTML = "";
    data.forEach(c => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>${c.email || ''}</td>
            <td>${c.phone || ''}</td>
            <td>${c.created_at}</td>
            <td>
                <button onclick="editCustomer(${c.id}, '${c.name}', '${c.email}', '${c.phone}')">Edit</button>
                <button onclick="deleteCustomer(${c.id})">Delete</button>
            </td>
        `;
        list.appendChild(tr);
    });
}

// Submit form
form.addEventListener("submit", async e => {
    e.preventDefault();
    const id = document.getElementById("customerId").value;
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;

    const payload = { name, email, phone };

    if (id) {
        await fetch(`/api/customers/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    } else {
        await fetch("/api/customers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
    }

    resetForm();
    loadCustomers();
});

// Edit customer
function editCustomer(id, name, email, phone) {
    document.getElementById("customerId").value = id;
    document.getElementById("name").value = name;
    document.getElementById("email").value = email || "";
    document.getElementById("phone").value = phone || "";
}

// Delete customer
async function deleteCustomer(id) {
    if (confirm("Are you sure you want to delete this customer?")) {
        await fetch(`/api/customers/${id}`, { method: "DELETE" });
        loadCustomers();
    }
}

// Reset form
function resetForm() {
    document.getElementById("customerId").value = "";
    form.reset();
}

resetBtn.addEventListener("click", resetForm);

// Load initial data
loadCustomers();
