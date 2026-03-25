"""
Personal Information Manager for SEEU AI
Stores and retrieves user's personal information locally
Prevents unnecessary internet searches for private data
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class PersonalInfoManager:
    """
    Manages user's personal information
    Stores data like: work, family, preferences, routines, etc.
    """

    def __init__(self, info_file: str = 'Database/personal_info.json'):
        """Initialize Personal Info Manager"""
        self.info_file = info_file
        self.data = self._load_personal_info()
        print("✅ Personal Info Manager initialized")

    def _load_personal_info(self) -> Dict:
        """Load personal information from JSON file"""
        if os.path.exists(self.info_file):
            try:
                with open(self.info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading personal info: {e}. Creating new file.")
                return self._create_default_structure()
        return self._create_default_structure()

    def _create_default_structure(self) -> Dict:
        """Create default personal info structure"""
        return {
            'basic_info': {
                'name': 'Narendra Sonawane',
                'age': '27',
                'birthday': '12 May 1998',
                'location': 'Pune, India',
                'phone': '',
                'email': ''
            },
            'work': {
                'company': 'Puneri Pattern PVT. LTD.',
                'position': '',
                'boss': 'Sarika mam',
                'team': '',
                'work_location': 'Magarpatta City, Pune',
                'work_hours': '',
                'projects': []
            },
            'family': {
                'spouse': '',
                'children': [],
                'parents': [],
                'siblings': []
            },
            'preferences': {
                'favorite_food': [],
                'favorite_music': [],
                'hobbies': [],
                'likes': [],
                'dislikes': []
            },
            'routines': {
                'morning_routine': '',
                'work_routine': '',
                'evening_routine': '',
                'weekend_routine': ''
            },
            'important_dates': {
                'anniversaries': [],
                'birthdays': [],
                'events': []
            },
            'contacts': {
                'friends': ["Ashwini","Ridhhi","Shradhha","Dimpal","Sushil","Krishna","Abhishek"],
                'colleagues': [],
                'emergency': []
            },
            'custom': {},
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }

    def _save_personal_info(self):
        """Save personal information to JSON file"""
        try:
            # Update metadata
            self.data['metadata']['last_updated'] = datetime.now().isoformat()

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.info_file) or '.', exist_ok=True)

            # Save to file
            with open(self.info_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving personal info: {e}")
            return False

    def set_info(self, category: str, key: str, value: Any) -> bool:
        """
        Set personal information

        Args:
            category: Category like 'work', 'family', 'preferences'
            key: Specific key like 'company', 'boss', etc.
            value: Value to store

        Returns:
            bool: Success status
        """
        try:
            if category not in self.data:
                self.data[category] = {}

            self.data[category][key] = value
            self._save_personal_info()
            print(f"✅ Saved: {category}.{key} = {value}")
            return True
        except Exception as e:
            print(f"❌ Error setting info: {e}")
            return False

    def get_info(self, category: str, key: str = None) -> Optional[Any]:
        """
        Get personal information

        Args:
            category: Category to retrieve
            key: Specific key (optional, returns whole category if None)

        Returns:
            Requested information or None
        """
        try:
            if category not in self.data:
                return None

            if key is None:
                return self.data[category]

            return self.data[category].get(key)
        except Exception as e:
            print(f"❌ Error getting info: {e}")
            return None

    def search_personal_info(self, query: str) -> Optional[str]:
        """
        Search personal information based on query

        Args:
            query: Natural language query

        Returns:
            Answer from personal info or None
        """
        query_lower = query.lower()

        # Work-related queries
        if any(word in query_lower for word in ['work', 'job', 'company', 'office']):
            if 'where' in query_lower or 'which company' in query_lower:
                company = self.get_info('work', 'company')
                if company:
                    return f"You work at {company}."

            if 'position' in query_lower or 'role' in query_lower or 'what do you do' in query_lower:
                position = self.get_info('work', 'position')
                company = self.get_info('work', 'company')
                if position and company:
                    return f"You work as a {position} at {company}."
                elif position:
                    return f"Your position is {position}."

        # Boss-related queries
        if any(word in query_lower for word in ['boss', 'manager', 'supervisor']):
            boss = self.get_info('work', 'boss')
            if boss:
                return f"Your boss is {boss}."

        # Team-related queries
        if 'team' in query_lower:
            team = self.get_info('work', 'team')
            if team:
                return f"You're on the {team} team."

        # Location queries
        if 'where do i live' in query_lower or 'my location' in query_lower:
            location = self.get_info('basic_info', 'location')
            if location:
                return f"You live in {location}."

        if 'work location' in query_lower or 'office location' in query_lower:
            work_location = self.get_info('work', 'work_location')
            if work_location:
                return f"Your office is in {work_location}."

        # Family queries
        if any(word in query_lower for word in ['wife', 'husband', 'spouse', 'partner']):
            spouse = self.get_info('family', 'spouse')
            if spouse:
                return f"Your spouse is {spouse}."

        if 'children' in query_lower or 'kids' in query_lower:
            children = self.get_info('family', 'children')
            if children and len(children) > 0:
                return f"You have {len(children)} children: {', '.join(children)}."

        # Contact queries
        if 'phone' in query_lower or 'mobile' in query_lower:
            phone = self.get_info('basic_info', 'phone')
            if phone:
                return f"Your phone number is {phone}."

        if 'email' in query_lower:
            email = self.get_info('basic_info', 'email')
            if email:
                return f"Your email is {email}."

        # Birthday queries
        if 'birthday' in query_lower or 'when was i born' in query_lower:
            birthday = self.get_info('basic_info', 'birthday')
            if birthday:
                return f"Your birthday is {birthday}."

        # Preference queries
        if 'favorite food' in query_lower:
            favorite_food = self.get_info('preferences', 'favorite_food')
            if favorite_food and len(favorite_food) > 0:
                return f"Your favorite foods are: {', '.join(favorite_food)}."

        if 'hobby' in query_lower or 'hobbies' in query_lower:
            hobbies = self.get_info('preferences', 'hobbies')
            if hobbies and len(hobbies) > 0:
                return f"Your hobbies include: {', '.join(hobbies)}."

        # Project queries
        if 'project' in query_lower:
            projects = self.get_info('work', 'projects')
            if projects and len(projects) > 0:
                return f"You're working on these projects: {', '.join(projects)}."

        return None  # No matching personal info found

    def quick_setup(self, user_data: Dict) -> bool:
        """
        Quick setup with all user data at once

        Args:
            user_data: Dictionary with all personal information

        Returns:
            bool: Success status
        """
        try:
            # Merge with existing data
            for category, values in user_data.items():
                if category == 'metadata':
                    continue

                if category not in self.data:
                    self.data[category] = {}

                if isinstance(values, dict):
                    self.data[category].update(values)
                else:
                    self.data[category] = values

            self._save_personal_info()
            print("✅ Personal information updated successfully")
            return True
        except Exception as e:
            print(f"❌ Error in quick setup: {e}")
            return False

    def get_summary(self) -> str:
        """Get a summary of stored personal information"""
        summary = "📋 Your Personal Information Summary\n"
        summary += "="*60 + "\n"

        # Basic Info
        name = self.get_info('basic_info', 'name')
        if name:
            summary += f"👤 Name: {name}\n"

        location = self.get_info('basic_info', 'location')
        if location:
            summary += f"📍 Location: {location}\n"

        # Work Info
        company = self.get_info('work', 'company')
        position = self.get_info('work', 'position')
        if company or position:
            summary += f"\n💼 Work:\n"
            if company:
                summary += f"  Company: {company}\n"
            if position:
                summary += f"  Position: {position}\n"

        boss = self.get_info('work', 'boss')
        if boss:
            summary += f"  Boss: {boss}\n"

        # Family
        spouse = self.get_info('family', 'spouse')
        if spouse:
            summary += f"\n👨‍👩‍👧‍👦 Family:\n"
            summary += f"  Spouse: {spouse}\n"

        children = self.get_info('family', 'children')
        if children and len(children) > 0:
            summary += f"  Children: {', '.join(children)}\n"

        # Preferences
        hobbies = self.get_info('preferences', 'hobbies')
        if hobbies and len(hobbies) > 0:
            summary += f"\n🎯 Hobbies: {', '.join(hobbies)}\n"

        return summary

    def export_template(self, template_file: str = 'Database/personal_info_template.json'):
        """Export a template file for easy editing"""
        template = self._create_default_structure()

        # Add helpful comments as values
        template['basic_info']['name'] = 'Your full name'
        template['work']['company'] = 'Your company name'
        template['work']['boss'] = 'Your boss/manager name'
        template['work']['position'] = 'Your job title'
        template['family']['spouse'] = 'Your spouse name'

        try:
            os.makedirs(os.path.dirname(template_file) or '.', exist_ok=True)
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✅ Template exported to: {template_file}")
            return True
        except Exception as e:
            print(f"❌ Error exporting template: {e}")
            return False


# Quick access functions
def setup_personal_info(user_data: Dict):
    """Quick function to setup personal info"""
    manager = PersonalInfoManager()
    return manager.quick_setup(user_data)


def get_personal_answer(query: str) -> Optional[str]:
    """Quick function to get answer from personal info"""
    manager = PersonalInfoManager()
    return manager.search_personal_info(query)


# Example usage and testing
if __name__ == "__main__":
    print("\n📋 SEEU Personal Information Manager - Test Mode")
    print("="*60)

    # Initialize manager
    manager = PersonalInfoManager()

    # Export template
    print("\n📝 Exporting template...")
    manager.export_template()

    # Example: Set some personal info
    print("\n✏️ Setting example personal information...")

    example_data = {
        'basic_info': {
            'name': 'Narendra Sonawane',
            'location': 'Pune, India',
            'email': '',
            'birthday': '12 May 1998'
        },
        'work': {
            'company': 'Puneri Pattern Pvt Ltd',
            'position': 'Internship',
            'boss': 'Sarika Mam',
            'team': '',
            'work_location': 'Magarpatta City, Pune',
            'projects': []
        },
        'family': {
            'spouse': '',
            'children': []
        },
        'preferences': {
            'favorite_food': [],
            'hobbies': []
        }
    }

    manager.quick_setup(example_data)

    # Test queries
    print("\n🧪 Testing Personal Info Queries:")
    print("="*60)

    test_queries = [
        "Where do I work?",
        "Who is my boss?",
        "What is my position?",
        "Where is my office?",
        "Who is my spouse?",
        "What are my hobbies?",
        "What projects am I working on?",
        "What's my favorite food?",
        "When is my birthday?"
    ]

    for query in test_queries:
        answer = manager.search_personal_info(query)
        print(f"\nQ: {query}")
        print(f"A: {answer if answer else 'No information found'}")

    # Show summary
    print("\n" + "="*60)
    print(manager.get_summary())
    print("="*60)

    print("\n✅ Personal Information Manager Ready!")
    print("\nTo use:")
    print("1. Edit Database/personal_info_template.json")
    print("2. Rename it to personal_info.json")
    print("3. SEEU will automatically use your personal data!")