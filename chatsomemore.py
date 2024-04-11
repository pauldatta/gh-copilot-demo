def reverse_string():
    # Get input from user
    input_string = input("Please enter a string: ")

    # Reverse the string
    reversed_string = input_string[::-1]

    # Print the reversed string
    print("The reversed string is:", reversed_string)

# Call the function
reverse_string()

def reverse_string(input_string):
    """Reverses the provided string and returns it."""
    return input_string[::-1]

def main():
    """Main function to execute the program."""
    # Get input from user
    input_string = input("Please enter a string: ")

    # Reverse the string
    reversed_string = reverse_string(input_string)

    # Print the reversed string
    print("The reversed string is:", reversed_string)

if __name__ == "__main__":
    main()