## Features

- Custom environent for buy and sell of crypto assets
- Custom dataloader with choosen metrics
- Test performance on future values
- Visualise buys, sells and portfolio value

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/ai-playground.git
    ```
2. Navigate to the project directory:
    ```sh
    cd ai-playground
    ```
3. Check out to branch:
    ```sh
    git switch model-with-portfolio-data
    ```
4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Go into jupyter notebooks and run cells one by one.

## Known problems

- Model avoids selling tokens somehow, need to adjust reward function to perform better.

## Considerations

- Use different metrics, some derivatives of these metrics, develop custom features.
- Add action of doing nothing instead of holding, to represent 4 actions
