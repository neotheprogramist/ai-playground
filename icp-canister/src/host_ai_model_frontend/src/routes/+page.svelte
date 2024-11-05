<script lang="ts">
  import "../index.scss";
  import { anonymousBackend } from "$lib/canisters";
  import { fetchData, Api } from "$lib/fetchData";

  let greeting = "";
  let apiKey = "";
  let symbol = "AAPL";
  let startDate = "2024-01-01";
  let endDate = "2024-01-05";

  async function onSubmit(event: Event) {
    try {
      const data = await fetchData(
        Api.ALPHA_VANTAGE,
        symbol,
        startDate,
        endDate,
        apiKey
      );
      console.log(data);
    } catch (error) {
      console.error(error);
      greeting = error instanceof Error ? error.message : "An error occurred";
    }
  }
</script>

<main>
  <img src="/logo2.svg" alt="DFINITY logo" />
  <br />
  <br />
  <form action="#" on:submit|preventDefault={onSubmit} class="form-container">
    <div class="form-group">
      <label for="symbol">Symbol:</label>
      <input 
        id="symbol"
        type="text"
        bind:value={symbol}
        placeholder="AAPL"
      />
    </div>

    <div class="form-group">
      <label for="startDate">Start Date:</label>
      <input 
        id="startDate"
        type="date"
        bind:value={startDate}
      />
    </div>

    <div class="form-group">
      <label for="endDate">End Date:</label>
      <input 
        id="endDate"
        type="date"
        bind:value={endDate}
      />
    </div>

    <div class="form-group">
      <label for="apiKey">API Key:</label>
      <input 
        id="apiKey"
        type="text"
        bind:value={apiKey}
        placeholder="Enter your Alpha Vantage API key"
      />
    </div>

    <button type="submit">Fetch Data</button>
  </form>

  {#if greeting}
    <section id="greeting" class="error-message">{greeting}</section>
  {/if}
</main>

<style>
  .form-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 400px;
    margin: 0 auto;
    padding: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  button:hover {
    background-color: #0056b3;
  }

  .error-message {
    color: #dc3545;
    margin-top: 1rem;
    text-align: center;
  }
</style>
