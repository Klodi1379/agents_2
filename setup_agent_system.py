#!/usr/bin/env python
"""
Agent System Setup Script

This script sets up the complete agent configuration system with LM Studio integration.
Run this after setting up the Django project to get the agent system ready for use.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("  🤖 AI Company - Agent System Setup")
    print("=" * 60)
    print()

def print_step(step, message):
    print(f"[STEP {step}] {message}")
    print("-" * 50)

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_django_setup():
    """Check if Django is properly set up"""
    print_step(1, "Checking Django Setup")
    
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the Django project root.")
        return False
    
    # Test Django settings
    success, output = run_command('python manage.py check --deploy')
    if not success:
        print("⚠️  Django setup has issues, but continuing...")
        print(f"   Output: {output}")
    else:
        print("✅ Django setup looks good!")
    
    return True

def apply_migrations():
    """Apply database migrations"""
    print_step(2, "Applying Database Migrations")
    
    # Apply general migrations
    success, output = run_command('python manage.py migrate')
    if not success:
        print(f"❌ Error applying migrations: {output}")
        return False
    
    print("✅ Database migrations applied successfully!")
    return True

def create_default_agents():
    """Create default agent configurations"""
    print_step(3, "Creating Default Agent Configurations")
    
    success, output = run_command('python manage.py create_default_agents')
    if not success:
        print(f"❌ Error creating default agents: {output}")
        return False
    
    print("✅ Default agent configurations created!")
    print("   Created agents:")
    print("   - Business Strategy Advisor")
    print("   - Financial Analysis Expert") 
    print("   - Market Research Analyst")
    return True

def check_lm_studio():
    """Check if LM Studio is running"""
    print_step(4, "Checking LM Studio Connection")
    
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ LM Studio is running!")
            if models.get('data'):
                print(f"   Available models: {len(models['data'])}")
                for model in models['data'][:3]:  # Show first 3 models
                    print(f"   - {model.get('id', 'Unknown')}")
            return True
        else:
            print(f"⚠️  LM Studio responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("⚠️  LM Studio is not running or not accessible")
        print("   Please start LM Studio and load a model before testing agents")
        return False

def test_agent_system():
    """Test the agent system"""
    print_step(5, "Testing Agent System")
    
    success, output = run_command('python test_agent_system.py')
    if not success:
        print(f"⚠️  Agent system test had issues: {output}")
        return False
    
    print("✅ Agent system test completed!")
    return True

def create_superuser_prompt():
    """Prompt to create a superuser if needed"""
    print_step(6, "Django Superuser Setup")
    
    try:
        # Check if any superusers exist
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_company.settings')
        django.setup()
        
        from django.contrib.auth.models import User
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists!")
            return True
    except:
        pass
    
    response = input("Would you like to create a Django superuser now? (y/n): ").lower().strip()
    if response == 'y':
        success, output = run_command('python manage.py createsuperuser')
        if success:
            print("✅ Superuser created successfully!")
        else:
            print("⚠️  Superuser creation was cancelled or failed")
    else:
        print("⚠️  Skipping superuser creation")
        print("   You can create one later with: python manage.py createsuperuser")
    
    return True

def show_next_steps():
    """Show what to do next"""
    print()
    print("=" * 60)
    print("  🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("1. Start LM Studio (if not already running):")
    print("   - Download from: https://lmstudio.ai/")
    print("   - Download a model (e.g., llama-2-7b-chat)")
    print("   - Load the model and start the local server")
    print("   - Ensure it's running on: http://localhost:1234")
    print()
    print("2. Start the Django development server:")
    print("   python manage.py runserver")
    print()
    print("3. Open your browser and navigate to:")
    print("   http://localhost:8000/agent-system/")
    print()
    print("4. Available agent system features:")
    print("   - Agent Configurations: Create and manage agents")
    print("   - Chat Interface: Talk to your agents")
    print("   - Agent Status: Monitor performance")
    print("   - LLM Providers: Configure different models")
    print()
    print("5. Test the system:")
    print("   - Use the 'Chat with Agent' button in the sidebar")
    print("   - Select an agent and start chatting")
    print("   - Try different agents for different tasks")
    print()
    print("6. Useful URLs:")
    print("   - Agent System: http://localhost:8000/agent-system/")
    print("   - Admin Panel: http://localhost:8000/admin/")
    print("   - Dashboard: http://localhost:8000/")
    print()
    print("📚 Documentation:")
    print("   - Agent System Guide: ./AGENT_SYSTEM_GUIDE.md")
    print("   - Test Script: python test_agent_system.py")
    print()
    print("🔧 Troubleshooting:")
    print("   - Check LM Studio is running on port 1234")
    print("   - Verify models are loaded in LM Studio")
    print("   - Check Django logs for any errors")
    print("   - Ensure all dependencies are installed")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    steps = [
        ("Django Setup Check", check_django_setup),
        ("Database Migrations", apply_migrations),
        ("Default Agents", create_default_agents),
        ("LM Studio Check", check_lm_studio),
        ("System Test", test_agent_system),
        ("Superuser Setup", create_superuser_prompt)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
            print()
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error in {step_name}: {str(e)}")
            results.append((step_name, False))
            print()
    
    # Summary
    print("=" * 60)
    print("  📊 Setup Summary")
    print("=" * 60)
    
    success_count = 0
    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {step_name:<25} {status}")
        if success:
            success_count += 1
    
    print()
    print(f"Successfully completed: {success_count}/{len(results)} steps")
    
    if success_count >= 4:  # At least core functionality working
        print("🎉 Agent system is ready to use!")
        show_next_steps()
    else:
        print("⚠️  Setup completed with issues. Please check the errors above.")
        print("   You may need to manually fix some issues before the system works properly.")

if __name__ == '__main__':
    main()