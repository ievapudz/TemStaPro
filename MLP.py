"""
Definition of the class of models with 2 hidden layers.
"""

from torch import nn

class MLP_C2H2(nn.Module):
    def __init__(self, input_size=None, hidden_size_1=None, hidden_size_2=None):
        if(input_size == None):
            self.input_size = 1280
        else:
            self.input_size = int(input_size)

        if(hidden_size_1 == None):
            self.hidden_size_1 = 640
        else:
            self.hidden_size_1 = int(hidden_size_1)

        if(hidden_size_2 == None):
            self.hidden_size_2 = 320
        else:
            self.hidden_size_2 = int(hidden_size_2)

        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(self.input_size, self.hidden_size_1),
            nn.ReLU(),
            nn.Linear(self.hidden_size_1, self.hidden_size_2),
            nn.ReLU(),
            nn.Linear(self.hidden_size_2, 2),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.layers(x)

