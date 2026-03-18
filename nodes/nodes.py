import canlecData as cld
import copy
import pygal

VOTECOUNTRIDINGTABLE = "VoteCountRidingTable"
COLLATEDVOTETABLE = "CollatedVoteTable"
RIDINGWINNERTABLE = "RidingWinnerTable"
COLLATEDSEATSTABLE = "CollatedSeatsTable"
IMAGE = "Image"
FLOAT = "Float"
PROVINCE = "Province"
PARTY = "Party"
ANYTABLE = "AnyTable"
ANYCOLLATEDTABLE = "AnyCollatedTable"
ANYRIDINGTABLE = "AnyRidingTable"

class node:
    def __init__(self, id: str = None, attrs: dict = None):
        self.id = id or "0"
        self.attrs = attrs or {}
        self.inputs = []
        self.outputs = []

    def connectInput(self, inputId, otherNode, outputId):
        self.inputs[inputId] = [self.inputs[inputId][0], otherNode, outputId]

    def compute(self):
        pass

## INPUT NODES

class floatNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.outputs = [[FLOAT, float(self.attrs.get("value", 0.0))]]

    def compute(self):
        print(self.outputs)
        pass

class dataSourceNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.outputs = [[VOTECOUNTRIDINGTABLE, cld.ridingTable]]

    def compute(self):
        pass

class provinceNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.outputs = [[PROVINCE, self.attrs.get("value", cld.PROVINCES[0])]]

    def compute(self):
        pass

class partyNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.outputs = [[PARTY, self.attrs.get("value", cld.PARTIES[0])]]

    def compute(self):
        pass

class noteNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = []
        self.outputs = []

    def compute(self):
        pass

## OUTPUT NODES

class barChartNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[ANYTABLE, None, None]]
        self.outputs = [[IMAGE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        inputType = self.inputs[0][1].outputs[self.inputs[0][2]][0]

        barChart = pygal.HorizontalBar()
        party_colors = {
            cld.LIBERAL: '#d71920',
            cld.CONSERVATIVE: '#003F72',
            cld.BLOC: '#ADD8E6',
            cld.NDP: '#F58220',
            cld.GREEN: '#24B24A'
        }

        if inputType == COLLATEDSEATSTABLE or inputType == COLLATEDVOTETABLE:
            # Data format: {"Liberal": 150, "Conservative": 120, ...}
            series_colors = []
            for party in startingData.keys():
                series_colors.append(party_colors.get(party, '#808080'))

            custom_style = pygal.style.Style(colors=tuple(series_colors))
            barChart.style = custom_style
            for party in startingData.keys():
                barChart.add(party, startingData[party])
                
        elif inputType == RIDINGWINNERTABLE:
            # Too many ridings to chart usefully as horizontal bar, maybe group by winner?
            counts = {}
            for r_id, r in startingData.items():
                winner = r.get("winner")
                counts[winner] = counts.get(winner, 0) + 1
            
            series_colors = []
            for party in counts.keys():
                series_colors.append(party_colors.get(party, '#808080'))

            custom_style = pygal.style.Style(colors=tuple(series_colors))
            barChart.style = custom_style
            for party in counts.keys():
                barChart.add(party, counts[party])
                
        else:
            # Too complex to bar chart VOTECOUNTRIDINGTABLE directly
            barChart.add("Not Supported", 1)

        svg_string = barChart.render(is_unicode=True)
        self.outputs = [[self.outputs[0][0], svg_string]]

class tableViewNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[ANYTABLE, None, None]]
        self.outputs = [[IMAGE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        inputType = self.inputs[0][1].outputs[self.inputs[0][2]][0]
        
        html = '<table style="width:100%; border-collapse: collapse; font-size: 0.8rem; background: white; color: black;">'
        
        if inputType == VOTECOUNTRIDINGTABLE:
            html += '<tr style="border-bottom: 2px solid #cbd5e0; background: #edf2f7;"><th style="text-align: left; padding: 6px;">Riding</th>'
            parties = []
            for r_id in startingData:
                parties = list(startingData[r_id]["partyResults"].keys())
                break
                
            for party in parties:
                html += f'<th style="text-align: right; padding: 6px;">{party}</th>'
            html += '</tr>'
            
            count = 0
            for r_id, riding in startingData.items():
                if count >= 5:
                    break
                bg_color = '#ffffff' if count % 2 == 0 else '#f7fafc'
                html += f'<tr style="border-bottom: 1px solid #e2e8f0; background: {bg_color};"><td style="padding: 6px;">{riding["name"]}</td>'
                for party in parties:
                    val = riding["partyResults"].get(party, 0)
                    html += f'<td style="text-align: right; padding: 6px; font-family: monospace;">{val}</td>'
                html += '</tr>'
                count += 1
                
        elif inputType == RIDINGWINNERTABLE:
            html += '<tr style="border-bottom: 2px solid #cbd5e0; background: #edf2f7;"><th style="text-align: left; padding: 6px;">Riding</th><th style="text-align: right; padding: 6px;">Winner</th></tr>'
            count = 0
            for r_id, riding in startingData.items():
                if count >= 5:
                    break
                bg_color = '#ffffff' if count % 2 == 0 else '#f7fafc'
                html += f'<tr style="border-bottom: 1px solid #e2e8f0; background: {bg_color};"><td style="padding: 6px;">{riding["name"]}</td><td style="text-align: right; padding: 6px;">{riding["winner"]}</td></tr>'
                count += 1
                
        elif inputType == COLLATEDSEATSTABLE or inputType == COLLATEDVOTETABLE:
            html += '<tr style="border-bottom: 2px solid #cbd5e0; background: #edf2f7;"><th style="text-align: left; padding: 6px;">Party</th><th style="text-align: right; padding: 6px;">Total</th></tr>'
            count = 0
            for party, total in startingData.items():
                if count >= 5:
                    break
                bg_color = '#ffffff' if count % 2 == 0 else '#f7fafc'
                html += f'<tr style="border-bottom: 1px solid #e2e8f0; background: {bg_color};"><td style="padding: 6px;">{party}</td><td style="text-align: right; padding: 6px; font-family: monospace;">{total}</td></tr>'
                count += 1
                
        else:
            html += '<tr><td>Unsupported Table Type</td></tr>'
            
        html += '</table>'
        self.outputs = [[self.outputs[0][0], html]]

class floatDisplayNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[FLOAT, None, None]]
        self.outputs = [[IMAGE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return

        val = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        
        html = f'<div style="padding: 10px; font-size: 1.5rem; font-weight: bold; text-align: center; color: black;">{val}</div>'
        self.outputs = [[self.outputs[0][0], html]]

## CONVERTER NODES

class findWinnerNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[VOTECOUNTRIDINGTABLE, None, None]]
        self.outputs = [[RIDINGWINNERTABLE, None]]
        
    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return
            
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
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[RIDINGWINNERTABLE, None, None]]
        self.outputs = [[COLLATEDSEATSTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]

        counts = {}
        for ridingID in startingData.keys():
            riding = startingData[ridingID]
            if riding["winner"] not in counts.keys():
                counts[riding["winner"]] = 0
            counts[riding["winner"]] += 1
        
        self.outputs = [[self.outputs[0][0], counts]]

class collateVotesNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [[VOTECOUNTRIDINGTABLE, None, None]]
        self.outputs = [[COLLATEDVOTETABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return

        startingData = self.inputs[0][1].outputs[self.inputs[0][2]][1]

        counts = {}
        for ridingID, riding in startingData.items():
            partyResults = riding["partyResults"]
            for party, votes in partyResults.items():
                if party not in counts:
                    counts[party] = 0
                counts[party] += votes
        
        self.outputs = [[self.outputs[0][0], counts]]


class extractCollatedNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [ANYCOLLATEDTABLE, None, None],
            [PARTY, None, None]
        ]
        self.outputs = [[FLOAT, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()
                
        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            self.outputs = [[FLOAT, 0.0]]
            return

        table = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        
        try:
            if self.inputs[1][1] is not None and self.inputs[1][2] is not None:
                party = self.inputs[1][1].outputs[self.inputs[1][2]][1]
                val = table.get(party, 0.0)
            else:
                val = sum(table.values())
        except Exception:
            val = 0.0

        self.outputs = [[FLOAT, float(val)]]

# SWING NODES

class uniformSwingNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [VOTECOUNTRIDINGTABLE, None, None],
            [FLOAT, None, None], # Lib
            [FLOAT, None, None], # Con
            [FLOAT, None, None], # NDP
            [FLOAT, None, None], # BQ
            [FLOAT, None, None], # Green
        ]
        self.outputs = [[VOTECOUNTRIDINGTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return
            
        base_table = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        
        # Get float inputs, defaulting to 0.0
        swings = []
        for i in range(1, 6):
            if self.inputs[i][1] is not None and self.inputs[i][2] is not None:
                swings.append(self.inputs[i][1].outputs[self.inputs[i][2]][1])
            else:
                swings.append(0.0)

        parties = cld.PARTIES
        
        output_table = copy.deepcopy(base_table)
        
        for ridingID, riding in output_table.items():
            party_results = riding["partyResults"]
            total_votes = sum(party_results.values())
            
            for i, party in enumerate(parties):
                swing_pts = swings[i]
                vote_change = (swing_pts / 100.0) * total_votes
                party_results[party] = max(0, int(round(party_results[party] + vote_change)))
            output_table[ridingID]["partyResults"] = party_results

        self.outputs = [[self.outputs[0][0], output_table]]


class proportionalSwingNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [VOTECOUNTRIDINGTABLE, None, None],
            [FLOAT, None, None], # Lib
            [FLOAT, None, None], # Con
            [FLOAT, None, None], # NDP
            [FLOAT, None, None], # BQ
            [FLOAT, None, None], # Green
        ]
        self.outputs = [[VOTECOUNTRIDINGTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None:
            return
            
        base_table = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        
        swings = []
        for i in range(1, 6):
            if self.inputs[i][1] is not None and self.inputs[i][2] is not None:
                swings.append(self.inputs[i][1].outputs[self.inputs[i][2]][1])
            else:
                swings.append(1.0) # Multiply by 1.0 (no change) by default

        parties = cld.PARTIES
        
        output_table = copy.deepcopy(base_table)
        
        for ridingID, riding in output_table.items():
            party_results = riding["partyResults"]
            
            for i, party in enumerate(parties):
                factor = swings[i]
                party_results[party] = max(0, int(round(party_results[party] * factor)))

        self.outputs = [[self.outputs[0][0], output_table]]

#COMBINE NODES

class mixVoteCountTableNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [VOTECOUNTRIDINGTABLE, None, None], # Table A
            [VOTECOUNTRIDINGTABLE, None, None], # Table B
            [FLOAT, None, None]                 # Factor
        ]
        self.outputs = [[VOTECOUNTRIDINGTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None or self.inputs[1][1] is None or self.inputs[1][2] is None:
            return
            
        table_a = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        table_b = self.inputs[1][1].outputs[self.inputs[1][2]][1]
        
        factor = 0.5
        if self.inputs[2][1] is not None and self.inputs[2][2] is not None:
            factor = self.inputs[2][1].outputs[self.inputs[2][2]][1]

        output_table = copy.deepcopy(table_a)
        
        for ridingID, riding_a in output_table.items():
            if ridingID in table_b:
                riding_b = table_b[ridingID]
                party_results_a = riding_a["partyResults"]
                party_results_b = riding_b["partyResults"]
                
                # We need to consider all parties that exist in A or B
                all_parties = set(party_results_a.keys()).union(set(party_results_b.keys()))
                
                for party in all_parties:
                    val_a = party_results_a.get(party, 0)
                    val_b = party_results_b.get(party, 0)
                    lerped_val = val_a * (1.0 - factor) + val_b * factor
                    party_results_a[party] = max(0, int(round(lerped_val)))

        self.outputs = [[self.outputs[0][0], output_table]]

class mergeTablesNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [ANYRIDINGTABLE, None, None],
            [ANYRIDINGTABLE, None, None]
        ]
        self.outputs = [[ANYRIDINGTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None or self.inputs[1][1] is None or self.inputs[1][2] is None:
            return
            
        table_a = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        table_b = self.inputs[1][1].outputs[self.inputs[1][2]][1]

        output_table = copy.deepcopy(table_a)
        
        for ridingID, riding_b in table_b.items():
            if ridingID not in output_table:
                output_table[ridingID] = copy.deepcopy(riding_b)

        self.outputs = [[self.outputs[0][0], output_table]]

## FILTER NODES

class filterProvinceNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [ANYRIDINGTABLE, None, None],
            [PROVINCE, None, None]
        ]
        self.outputs = [[ANYRIDINGTABLE, None], [ANYRIDINGTABLE, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        if self.inputs[0][1] is None or self.inputs[0][2] is None or self.inputs[1][1] is None or self.inputs[1][2] is None:
            return
            
        base_table = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        province = self.inputs[1][1].outputs[self.inputs[1][2]][1]
        
        output_table1 = {}
        output_table2 = {}
        for ridingID, riding in base_table.items():
            if riding["province"] == province:
                output_table1[ridingID] = copy.deepcopy(riding)
            else:
                output_table2[ridingID] = copy.deepcopy(riding)

        inputType = self.inputs[0][1].outputs[self.inputs[0][2]][0]
        self.outputs = [[inputType, output_table1], [inputType, output_table2]]

## MATH NODES

class divideNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [FLOAT, None, None],
            [FLOAT, None, None]
        ]
        self.outputs = [[FLOAT, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        val1 = 0.0
        if self.inputs[0][1] is not None and self.inputs[0][2] is not None:
            val1 = self.inputs[0][1].outputs[self.inputs[0][2]][1]
            
        val2 = 1.0
        if self.inputs[1][1] is not None and self.inputs[1][2] is not None:
            val2 = self.inputs[1][1].outputs[self.inputs[1][2]][1]

        if val2 == 0:
            res = 0.0
        else:
            res = val1 / val2

        self.outputs = [[FLOAT, res]]

class multiplyNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [FLOAT, None, None],
            [FLOAT, None, None]
        ]
        self.outputs = [[FLOAT, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        val1 = 1.0
        if self.inputs[0][1] is not None and self.inputs[0][2] is not None:
            val1 = self.inputs[0][1].outputs[self.inputs[0][2]][1]
        elif self.inputs[1][1] is not None:
            val1 = 1.0
        else:
            val1 = 0.0
            
        val2 = 1.0
        if self.inputs[1][1] is not None and self.inputs[1][2] is not None:
            val2 = self.inputs[1][1].outputs[self.inputs[1][2]][1]
        elif self.inputs[0][1] is not None:
            val2 = 1.0
        else:
            val2 = 0.0

        self.outputs = [[FLOAT, val1 * val2]]

class addNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [FLOAT, None, None],
            [FLOAT, None, None]
        ]
        self.outputs = [[FLOAT, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        val1 = 0.0
        if self.inputs[0][1] is not None and self.inputs[0][2] is not None:
            val1 = self.inputs[0][1].outputs[self.inputs[0][2]][1]
            
        val2 = 0.0
        if self.inputs[1][1] is not None and self.inputs[1][2] is not None:
            val2 = self.inputs[1][1].outputs[self.inputs[1][2]][1]

        self.outputs = [[FLOAT, val1 + val2]]

class subtractNode(node):
    def __init__(self, id: str = None, attrs: dict = None):
        super().__init__(id, attrs)
        self.inputs = [
            [FLOAT, None, None],
            [FLOAT, None, None]
        ]
        self.outputs = [[FLOAT, None]]

    def compute(self):
        for ip in self.inputs:
            if ip[1] is not None:
                ip[1].compute()

        val1 = 0.0
        if self.inputs[0][1] is not None and self.inputs[0][2] is not None:
            val1 = self.inputs[0][1].outputs[self.inputs[0][2]][1]
            
        val2 = 0.0
        if self.inputs[1][1] is not None and self.inputs[1][2] is not None:
            val2 = self.inputs[1][1].outputs[self.inputs[1][2]][1]

        self.outputs = [[FLOAT, val1 - val2]]






NODE_TYPES = {
    "floatNode": floatNode,
    "dataSourceNode": dataSourceNode,
    "findWinnerNode": findWinnerNode,
    "collateWinnersNode": collateWinnersNode,
    "barChartNode": barChartNode,
    "uniformSwingNode": uniformSwingNode,
    "proportionalSwingNode": proportionalSwingNode,
    "mixVoteCountTableNode": mixVoteCountTableNode,
    "provinceNode": provinceNode,
    "filterProvinceNode": filterProvinceNode,
    "mergeTablesNode": mergeTablesNode,
    "divideNode": divideNode,
    "multiplyNode": multiplyNode,
    "addNode": addNode,
    "subtractNode": subtractNode,
    "collateVotesNode": collateVotesNode,
    "tableViewNode": tableViewNode,
    "partyNode": partyNode,
    "noteNode": noteNode,
    "extractCollatedNode": extractCollatedNode,
    "floatDisplayNode": floatDisplayNode
}
