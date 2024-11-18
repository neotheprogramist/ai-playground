import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomCombinedExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super(CustomCombinedExtractor, self).__init__(observation_space, features_dim)

        self._observation_space = observation_space
        
        price_shape = observation_space['prices'].shape
        portfolio_shape = observation_space['portfolio'].shape
        
        self.price_net = nn.LSTM(
            input_size=price_shape[1],
            hidden_size=64,
            num_layers=1,
            batch_first=True,
            # dropout=0.3
        )
        
        self.portfolio_net = nn.Sequential(
            nn.Linear(portfolio_shape[0], 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU()
        )
        
        lstm_output_dim = 64
        portfolio_output_dim = 32
        
        self._features_dim = lstm_output_dim + portfolio_output_dim
    
    def forward(self, observations):
        price_seq = observations['prices']
        batch_size = price_seq.shape[0]
        
        lstm_out, (h_n, c_n) = self.price_net(price_seq)
        lstm_last_output = lstm_out[:, -1, :]
        
        portfolio_out = self.portfolio_net(observations['portfolio'])
        
        combined = torch.cat((lstm_last_output, portfolio_out), dim=1)
        return combined