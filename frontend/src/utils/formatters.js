export function formatCurrency(value) {
  if (value === null || value === undefined || value === "") return "R$ 0,00";
  const num = typeof value === "number" ? value : parseFloat(value);
  if (isNaN(num)) return "R$ 0,00";
  
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatDateBR(dateStr) {
  if (!dateStr) return "—";
  if (dateStr.includes("/")) return dateStr;
  
  const parts = dateStr.split("-");
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
}

export function formatPercent(value) {
  const num = typeof value === "number" ? value : parseFloat(value);
  if (isNaN(num)) return "0.0%";
  return `${num.toFixed(1)}%`;
}
