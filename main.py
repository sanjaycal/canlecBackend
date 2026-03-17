import canlecData as cld
import random
import pygal

VOTECOUNTRIDINGTABLE = "VoteCountRidingTable"
RIDINGWINNERTABLE = "RidingWinnerTable"
COLLATEDSEATSTABLE = "CollatedSeatsTable"
IMAGE = "Image"

class node:
    id = "0"
    inputs = []
    
    outputs = []

    def compute(self):
        pass

class dataSourceNode(node):
    def __init__(self):
        self.id = str(random.randint(1,1000_000_000))

        self.inputs = []
        
        self.outputs = [[VOTECOUNTRIDINGTABLE, cld.ridingTable]]

    def compute(self):
        pass

class findWinnerNode(node):
    def __init__(self):
        self.id = str(random.randint(1,1000_000_000))

        self.inputs = [[VOTECOUNTRIDINGTABLE, None, None]]
        
        self.outputs = [[RIDINGWINNERTABLE, None]]
        
    def connectInput(self, inputId, otherNode, outputId):
        self.inputs[inputId] = [self.inputs[inputId][0], otherNode, outputId]
        
    def compute(self):
        for ip in self.inputs:
            ip[1].compute()

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        outputData = {}

        for ridingID in startingData.keys():
            riding = startingData[ridingID]
            outputData[riding["number"]] = {
                "name": riding["name"],
                "province": riding["province"],
                "number": riding["number"],
                "winner": max(riding["partyResults"], key = riding["partyResults"].get)
            }

        self.outputs = [[self.outputs[0][0], outputData]]
            
class collateWinnersNode(node):
    def __init__(self):
        self.id = str(random.randint(1,1000_000_000))

        self.inputs = [[RIDINGWINNERTABLE, None, None]]
        
        self.outputs = [[COLLATEDSEATSTABLE, None]]

    def connectInput(self, inputId, otherNode, outputId):
        self.inputs[inputId] = [self.inputs[inputId][0], otherNode, outputId]
        
    def compute(self):
        for ip in self.inputs:
            ip[1].compute()

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]

        counts = {}
        for ridingID in startingData.keys():
            riding = startingData[ridingID]
            if riding["winner"] not in counts.keys():
                counts[riding["winner"]] = 0
            counts[riding["winner"]] += 1
        
        self.outputs = [[self.outputs[0][0], counts]]

class barChartSeatsNode(node):
    def __init__(self):
        self.id = str(random.randint(1,1000_000_000))

        self.inputs = [[COLLATEDSEATSTABLE, None, None]]
        
        self.outputs = [[IMAGE, None]]

    def connectInput(self, inputId, otherNode, outputId):
        self.inputs[inputId] = [self.inputs[inputId][0], otherNode, outputId]
        
    def compute(self):
        for ip in self.inputs:
            ip[1].compute()

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]

        barChart = pygal.HorizontalBar()
        for party in startingData.keys():
            barChart.add(party, startingData[party])

        barChart.render_to_file('bar_chart.svg')
        
        self.outputs = [[self.outputs[0][0], None]]


def main():
    node1 = dataSourceNode()
    node2 = findWinnerNode()
    node3 = collateWinnersNode()
    node4 = barChartSeatsNode()
    node2.connectInput(0, node1, 0)
    node3.connectInput(0, node2, 0)
    node4.connectInput(0, node3, 0)
    node4.compute()

    print(node3.outputs[0][1])


if __name__ == "__main__":
    main()
