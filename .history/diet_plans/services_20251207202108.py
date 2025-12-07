from .models import DietPlan


class DietPlanGenerator:
    def __init__(self, user_profile):
        self.profile = user_profile

    def calculate_bmr(self):
        if not all([self.profile.age, self.profile.height, self.profile.current_weight, self.profile.gender]):
            return None

        if self.profile.gender == 'male':
            bmr = 88.362 + (13.397 * self.profile.current_weight) + (4.799 * self.profile.height) - (5.677 * self.profile.age)
        else:
            bmr = 447.593 + (9.247 * self.profile.current_weight) + (3.098 * self.profile.height) - (4.330 * self.profile.age)

        return round(bmr, 2)

    def calculate_tdee(self, bmr):
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        multiplier = activity_multipliers.get(self.profile.activity_level, 1.2)
        return round(bmr * multiplier, 2)

    def adjust_calories_for_goal(self, tdee, goal_type):
        if goal_type == 'weight_loss':
            return int(tdee - 500)
        if goal_type == 'weight_gain':
            return int(tdee + 500)
        return int(tdee)

    def generate_meal_plan(self, daily_calories, goal_type):
        meals = {
            'breakfast': {
                'name': 'Breakfast',
                'calories': int(daily_calories * 0.25),
                'foods': []
            },
            'lunch': {
                'name': 'Lunch',
                'calories': int(daily_calories * 0.35),
                'foods': []
            },
            'dinner': {
                'name': 'Dinner',
                'calories': int(daily_calories * 0.30),
                'foods': []
            },
            'snacks': {
                'name': 'Snacks',
                'calories': int(daily_calories * 0.10),
                'foods': []
            }
        }

        if goal_type == 'weight_loss':
            meals['breakfast']['foods'] = [
                'Oatmeal with berries (200 cal)',
                'Greek yogurt with honey (150 cal)',
                'Whole grain toast with avocado (180 cal)'
            ]
            meals['lunch']['foods'] = [
                'Grilled chicken salad (350 cal)',
                'Quinoa bowl with vegetables (320 cal)',
                'Lentil soup with whole grain bread (380 cal)'
            ]
            meals['dinner']['foods'] = [
                'Baked salmon with vegetables (400 cal)',
                'Turkey stir-fry with brown rice (420 cal)',
                'Vegetable curry with quinoa (380 cal)'
            ]
            meals['snacks']['foods'] = [
                'Apple with almond butter (120 cal)',
                'Protein bar (150 cal)',
                'Mixed nuts (100 cal)'
            ]
        else:
            meals['breakfast']['foods'] = [
                'Protein smoothie with banana (400 cal)',
                'Eggs with whole grain toast (350 cal)',
                'Greek yogurt parfait with granola (380 cal)'
            ]
            meals['lunch']['foods'] = [
                'Chicken and rice bowl (550 cal)',
                'Pasta with meat sauce (600 cal)',
                'Burrito bowl with extra protein (580 cal)'
            ]
            meals['dinner']['foods'] = [
                'Steak with sweet potato (650 cal)',
                'Salmon with rice and vegetables (620 cal)',
                'Chicken curry with naan (600 cal)'
            ]
            meals['snacks']['foods'] = [
                'Protein shake (250 cal)',
                'Trail mix (200 cal)',
                'Peanut butter sandwich (280 cal)'
            ]

        return meals

    def generate(self):
        if not self.profile.fitness_goal:
            return None

        bmr = self.calculate_bmr()
        if not bmr:
            return None

        tdee = self.calculate_tdee(bmr)
        daily_calories = self.adjust_calories_for_goal(tdee, self.profile.fitness_goal)
        meals = self.generate_meal_plan(daily_calories, self.profile.fitness_goal)

        diet_plan, _ = DietPlan.objects.update_or_create(
            user=self.profile.user,
            goal_type=self.profile.fitness_goal,
            defaults={
                'daily_calories': daily_calories,
                'meals': meals
            }
        )

        return diet_plan
