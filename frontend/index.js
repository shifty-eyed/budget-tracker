const API_BASE_URL = window.APP_CONFIG?.apiBaseUrl ?? 'http://localhost:8000';
const USER_ID = 'demo-user';

const linkButton = document.getElementById('link-button');
const refreshButton = document.getElementById('refresh-button');
const statusMessage = document.getElementById('status-message');
const transactionsBody = document.getElementById('transactions-body');

let linkHandler = null;
let creatingLinkToken = false;

function setStatus(message, type = 'info') {
  statusMessage.textContent = message;
  statusMessage.dataset.type = type;
}

function formatAmount(amount) {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  });
  return formatter.format(amount);
}

function formatDate(isoDate) {
  try {
    return new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(
      new Date(isoDate),
    );
  } catch (error) {
    return isoDate;
  }
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  const contentType = response.headers.get('content-type') || '';
  const isJSON = contentType.includes('application/json');
  const payload = isJSON ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail || response.statusText;
    throw new Error(detail || 'Request failed');
  }

  return payload;
}

function renderTransactions(transactions) {
  transactionsBody.innerHTML = '';

  if (!transactions.length) {
    const row = document.createElement('tr');
    row.className = 'placeholder-row';
    const cell = document.createElement('td');
    cell.colSpan = 4;
    cell.textContent = 'No transactions available for this item yet.';
    row.appendChild(cell);
    transactionsBody.appendChild(row);
    return;
  }

  transactions.forEach((transaction) => {
    const row = document.createElement('tr');

    const dateCell = document.createElement('td');
    dateCell.textContent = formatDate(transaction.date);
    row.appendChild(dateCell);

    const nameCell = document.createElement('td');
    nameCell.textContent = transaction.name || 'Unknown merchant';
    row.appendChild(nameCell);

    const categoryCell = document.createElement('td');
    const categories = transaction.category || [];
    categoryCell.textContent = categories.join(' • ') || 'Uncategorized';
    row.appendChild(categoryCell);

    const amountCell = document.createElement('td');
    amountCell.className = 'amount-column';
    const amount = transaction.amount || 0;
    amountCell.textContent = formatAmount(amount);
    amountCell.classList.toggle('negative-amount', amount > 0);
    amountCell.classList.toggle('positive-amount', amount < 0);
    row.appendChild(amountCell);

    transactionsBody.appendChild(row);
  });
}

async function fetchTransactions() {
  setStatus('Fetching latest transactions…');
  refreshButton.disabled = true;

  try {
    const query = new URLSearchParams({ user_id: USER_ID });
    const { transactions } = await fetchJSON(
      `${API_BASE_URL}/api/transactions?${query.toString()}`,
    );
    renderTransactions(transactions);
    setStatus('Transactions updated.', 'success');
  } catch (error) {
    console.error(error);
    setStatus(error.message || 'Unable to fetch transactions.', 'error');
  } finally {
    refreshButton.disabled = false;
  }
}

async function exchangePublicToken(publicToken) {
  setStatus('Exchanging public token for an access token…');
  refreshButton.disabled = true;

  try {
    await fetchJSON(`${API_BASE_URL}/api/set_access_token`, {
      method: 'POST',
      body: JSON.stringify({
        public_token: publicToken,
        user_id: USER_ID,
      }),
    });
    setStatus('Bank account linked. Loading transactions…', 'success');
    await fetchTransactions();
    refreshButton.disabled = false;
    refreshButton.focus();
  } catch (error) {
    console.error(error);
    setStatus(error.message || 'Failed to exchange public token.', 'error');
  }
}

async function openPlaidLink() {
  if (creatingLinkToken) {
    return;
  }

  creatingLinkToken = true;
  setStatus('Creating a new Plaid link token…');
  linkButton.disabled = true;

  try {
    const response = await fetchJSON(`${API_BASE_URL}/api/create_link_token`, {
      method: 'POST',
      body: JSON.stringify({ user_id: USER_ID }),
    });

    linkHandler = window.Plaid.create({
      token: response.link_token,
      onSuccess: async (publicToken) => {
        await exchangePublicToken(publicToken);
      },
      onExit: (err) => {
        if (err) {
          console.error(err);
          setStatus(err.display_message || err.error_message || 'Link flow exited.', 'error');
        } else {
          setStatus('Link flow exited before completion.');
        }
      },
    });

    linkHandler.open();
  } catch (error) {
    console.error(error);
    setStatus(error.message || 'Unable to create link token.', 'error');
  } finally {
    creatingLinkToken = false;
    linkButton.disabled = false;
  }
}

linkButton.addEventListener('click', () => {
  if (linkHandler) {
    linkHandler.open();
    return;
  }

  openPlaidLink();
});

refreshButton.addEventListener('click', () => {
  fetchTransactions();
});

setStatus('Ready when you are. Connect a bank account to get started.');
