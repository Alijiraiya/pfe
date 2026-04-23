class WaterFillingDistribution:
    def __init__(self, total_budget, reserve=0.1, min_amt=1000, max_amt=10000):
        self.total_budget = total_budget
        self.reserve = reserve
        self.min_amt = min_amt
        self.max_amt = max_amt
        self.net_budget = total_budget * (1 - reserve)

    def calculate(self, families):
        if not families:
            return {'success': False, 'message': 'Aucune famille'}
        
        total_svf = sum(f.get('svf_score', 0) for f in families)
        if total_svf == 0:
            return {'success': False, 'message': 'Somme SVF nulle'}

        distributions = []
        for f in families:
            raw_amount = self.net_budget * (f.get('svf_score', 0) / total_svf)
            final_amount = max(self.min_amt, min(self.max_amt, raw_amount))
            distributions.append({
                'family_id': f['id'],
                'head_name': f['head_name'],
                'svf_score': f.get('svf_score', 0),
                'amount': round(final_amount, 2)
            })

        return {
            'success': True,
            'total_budget': self.total_budget,
            'net_budget': self.net_budget,
            'distributions': distributions
        }