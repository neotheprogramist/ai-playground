<script lang="ts">
  import { anonymousBackend } from "$lib/canisters";
  import { fetchData, Api } from "$lib/fetchData";
  import type { Action } from "../../../declarations/host_ai_model_backend/host_ai_model_backend.did";
  import { TradingEnvironment, type TradingData } from "$lib/env";
  import Line from "../components/Line.svelte";
  import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
  } from "chart.js";

  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );

  let greeting = $state("");
  let apiKey = $state("");
  let symbol = $state("AAPL");
  let startDate = $state("2024-01-01");
  let endDate = $state("2024-01-05");
  let isLoading = $state(false);
  let portfolioValues: number[] = $state([]);
  let actions: string[] = $state([]);
  let dates: string[] = $state([]);

  // Chart data
  let chartData = $derived({
    labels: dates,
    datasets: [
      {
        label: "Portfolio Value", 
        data: portfolioValues,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  });

  let chartOptions = $derived({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
      },
      title: {
        display: true,
        text: "Portfolio Value Over Time",
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Date",
        },
      },
      y: {
        title: {
          display: true,
          text: "Portfolio Value ($)",
        },
      },
    },
  });

  function actionToNumber(action: Action): number {
    if ("Buy" in action) return 0;
    if ("Hold" in action) return 1;
    if ("Sell" in action) return 2;
    return 1;
  }

  function actionToString(action: Action): string {
    if ("Buy" in action) return "Buy";
    if ("Hold" in action) return "Hold";
    if ("Sell" in action) return "Sell";
    return "Hold";
  }

  async function predictIC(observation: number[]): Promise<Action> {
    try {
      const response = await anonymousBackend.get_action(observation);
      if ("Err" in response) {
        throw new Error(response.Err);
      }
      return response.Ok;
    } catch (error) {
      console.error("Error predicting action:", error);
      throw error;
    }
  }

  async function testICModel(env: TradingEnvironment): Promise<void> {
    portfolioValues = [];
    actions = [];
    dates = [];
    let observation = env.reset();
    console.log("Starting test with initial observation:", observation);

    while (true) {
      try {
        const action = await predictIC(observation);
        console.log("Predicted action:", action);
        const actionStr = actionToString(action);
        console.log("Action as string:", actionStr);

        actions = [...actions, actionStr];

        const {
          observation: newObs,
          reward,
          done,
          info,
        } = env.step(actionToNumber(action));
        console.log("Step result:", { newObs, reward, done, info });

        const currentDate = info.prediction_date.toLocaleDateString();
        dates = [...dates, currentDate];
        portfolioValues = [...portfolioValues, info.portfolio_value];

        if (done) {
          console.log("Simulation complete. Total steps:", actions.length);
          break;
        }

        observation = newObs;
      } catch (error) {
        console.error("Error during testing:", error);
        break;
      }
    }

    console.log("Final actions:", actions);
    console.log("Final portfolio values:", portfolioValues);
  }

  async function onSubmit(event: Event) {
    isLoading = true;
    greeting = "";

    try {
      const data = await fetchData(
        Api.ALPHA_VANTAGE,
        symbol,
        startDate,
        endDate,
        apiKey
      );
      const env = new TradingEnvironment(data, 10000, startDate);
      await testICModel(env);
    } catch (error) {
      console.error(error);
      greeting = error instanceof Error ? error.message : "An error occurred";
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="main-container">
  <div class="two-column-layout">
    <div class="config-column">
      <form
        action="#"
        onsubmit={onSubmit}
        class="form-container"
      >
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
          <input id="startDate" type="date" bind:value={startDate} />
        </div>

        <div class="form-group">
          <label for="endDate">End Date:</label>
          <input id="endDate" type="date" bind:value={endDate} />
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

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Processing..." : "Fetch Data"}
        </button>
      </form>
    </div>

    <div class="chart-column">
      {#if portfolioValues.length > 0}
        <div class="chart-container">
          <Line data={chartData} options={chartOptions} />
        </div>
      {/if}
    </div>
  </div>
  <div class="actions-container">
    {#if greeting}
      <section id="greeting" class="error-message">{greeting}</section>
    {/if}

    <h3>Trading Actions</h3>

    {#if actions.length > 0}
      <div class="actions-list">
        <div class="actions-grid">
          {#each actions as action, i}
            <div class="action-item">
              <span class="step">{dates[i]}:</span>
              <span class="action {action.toLowerCase()}">{action}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  .main-container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    gap: 2rem;
  }

  .two-column-layout {
    display: grid;
    grid-template-columns: 1fr 3fr;
    gap: 2rem;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .config-column {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    height: fit-content;
  }

  .chart-column {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .chart-container {
    height: 600px;
    width: 100%;
    margin-bottom: 2rem;
  }

  @media (max-width: 1024px) {
    .two-column-layout {
      grid-template-columns: 1fr;
    }

    .chart-container {
      height: 400px;
    }
  }

  .form-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 400px;
    margin: 0 auto;
    padding: 1rem;
    margin: 0;
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

  button:disabled {
    background-color: #cccccc;
  }

  button:hover:not(:disabled) {
    background-color: #0056b3;
  }

  .error-message {
    color: #e53345;
    margin-top: 1rem;
    text-align: center;
    font-weight: bold;
  }

  .actions-container {
    margin-top: 1rem;
    padding: 2rem;
  }

  .actions-list {
    background-color: #fcfbfcd3;
    padding: 2rem;
    border-radius: 4px;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 0.5rem;
  }

  .action-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background-color: rgb(245, 242, 242);
    border-radius: 7px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .step {
    font-weight: bold;
    color: #000000;
  }

  .action {
    padding: 0.5rem 0.5rem;
    border-radius: 3px;
    font-weight: bold;
  }

  .buy {
    background-color: #97e2a9;
    color: #1f592c;
  }

  .sell {
    background-color: #f8d7da;
    color: #8e1723;
  }

  .hold {
    background-color: #e7d087;
    color: #866a19;
  }
</style>
