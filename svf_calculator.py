class SVFCalculator:
    SMIG = 20000

    @classmethod
    def calculate(cls, family_data):
        score = 0
        income = family_data.get('monthly_income', 0)
        if income < cls.SMIG: score += 40
        elif income < 2 * cls.SMIG: score += 30
        elif income < 3 * cls.SMIG: score += 15
        
        score += family_data.get('children_count', 0) * 5
        
        # البحث في النصوص المزدوجة بأمان
        social_status = family_data.get('social_status', '')
        if 'Veuve' in social_status or 'Divorce' in social_status: score += 10
        elif 'Orphelin' in social_status: score += 15

        health = family_data.get('health_status', 'Bonne')
        if 'Maladie chronique' in health: score += 10
        elif 'Handicap' in health: score += 15

        is_renting = family_data.get('is_renting', '')
        if 'Oui' in is_renting: score += 10
        if family_data.get('benefit_count', 0) > 0: score -= 5

        return round(min(max(score, 0), 100), 2)

    @staticmethod
    def get_category(score):
        if score >= 80: return "Urgent | عاجل"
        elif score >= 60: return "Vulnérable | هش"
        elif score >= 40: return "Modéré | متوسط"
        return "Faible | أولوية ضعيفة"