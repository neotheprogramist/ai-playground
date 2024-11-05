interface EnvInfo {
    total_reward: number;
    balance: number;
    portfolio_value: number;
    prediction_date: Date;

  }
  
  interface StepResult {
    observation: number[];
    reward: number;
    done: boolean;
    truncated: boolean;
    info: EnvInfo;
  }

  export interface TradingData {
    Open: number;
    High: number;
    Low: number;
    Close: number;
    Volume: number;
  }

  function addDays(date: Date, days: number): Date {
    return new Date(date.setDate(date.getDate() + days));
  }
  
  export class TradingEnvironment {
    private data: TradingData[]; // Replace 'any' with proper data interface
    private currentStep: number = 0;
    private totalReward: number = 0;
    private balance: number;
    private tokenAmount: number = 0;
    private balanceBeforeSell: number = 0;
    private readonly pctOfBalance: number = 0.1;
    private predictionDate: Date;
    constructor(data: any[], initialBalance: number = 10000, startDate: string) {
      this.data = data;
      this.balance = initialBalance;
      this.predictionDate = new Date(startDate);
    }
  
    private getNextObservation(): number[] {
      const currentData = this.data[this.currentStep];
      return [
        currentData.Open,
        currentData.High,
        currentData.Low,
        currentData.Close,
        currentData.Volume
      ];
    }
  
    private getInfo(): EnvInfo {
      return {
        total_reward: this.totalReward,
        balance: this.balance,
        portfolio_value: this.balance + (this.tokenAmount * this.data[this.currentStep].Close),
        prediction_date: addDays(new Date(this.predictionDate), this.currentStep)
      };
    }

    reset(): number[] {
      this.currentStep = 0;
      this.totalReward = 0;
      return this.getNextObservation();
    }
  
    step(action: number): StepResult {
      const currentPrice = this.data[this.currentStep].Close;
      if (currentPrice <= 0) {
        throw new Error("Invalid current price encountered in data.");
      }
      let reward = 0;
  
      switch (action) {
        case 0: // Buy
          if (this.balance * this.pctOfBalance > 0) {
            this.tokenAmount += (this.balance * this.pctOfBalance) / currentPrice;
            this.balance -= this.balance * this.pctOfBalance;
            reward = 0.01;
          } else if (this.balance < 0) {
            reward = -0.5;
          }
          break;
  
        case 1: // Hold
          reward = 0.1;
          break;
  
        case 2: // Sell
          if (this.tokenAmount > 0) {
            this.balanceBeforeSell = this.balance;
            this.balance += this.tokenAmount * currentPrice;
            this.tokenAmount = 0;
            reward = (this.balance - this.balanceBeforeSell) / 1000;
          } else {
            reward = -0.5;
          }
          break;
      }
  
      this.currentStep += 1;
      const done = this.currentStep >= this.data.length - 1;
      const observation = this.getNextObservation();
      this.totalReward += reward;

      return {
        observation,
        reward,
        done,
        truncated: false,
        info: this.getInfo()
      };
    }
  }