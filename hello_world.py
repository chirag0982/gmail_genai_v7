#!/usr/bin/env python3
"""
Hello World Python Program
A simple introduction to Python programming

This program demonstrates:
- Basic Python syntax
- Print function usage
- Comments and documentation
- Error handling basics
"""

def main():
    """
    Main function that prints the Hello World message
    
    This function demonstrates:
    - Function definition
    - Docstrings for documentation
    - Basic output with print()
    """
    try:
        # Print the classic "Hello, World!" message
        print("Hello, World!")
        
        # Additional examples for learning
        print("Welcome to Python programming!")
        print("=" * 30)  # Print a separator line
        
        # Demonstrate basic variable usage
        message = "Python is awesome!"
        print(f"Message: {message}")
        
        # Show different ways to print
        name = "Learner"
        print(f"Hello, {name}! Ready to learn Python?")
        
    except Exception as error:
        # Basic error handling demonstration
        print(f"An error occurred: {error}")
        return 1
    
    return 0

# This block ensures the main function runs only when the script is executed directly
# not when it's imported as a module
if __name__ == "__main__":
    # Call the main function and exit with its return code
    exit_code = main()
    exit(exit_code)
