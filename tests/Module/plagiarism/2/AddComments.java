import java.io.*;
import java.util.*;

public class AddComments {

    // ArrayList to store expressions read from the input file.
    public ArrayList<String> inputExpressions;
    // ArrayList to store results of the calculations.
    public ArrayList<String> calculationResults;

    // Constructor of the class.
    public AddComments() {
        inputExpressions = new ArrayList<>(); // Initialize the list of input expressions.
        calculationResults = new ArrayList<>(); // Initialize the list of calculation results.
    }

    // Method to start the calculation process.
    public void calculate(String path) {
        read_file(path); // Read expressions from the file.
        // Iterate over each expression for calculation.
        for (String expression : inputExpressions) {
            cal(expression); // Calculate the result of the current expression.
        }
        write_file("Out.txt"); // Write the calculation results to an output file.
    }

    // Method to calculate a single expression.
    public void cal(String expression) {
        // Check for invalid start or end characters.
        if (!Character.isDigit(expression.charAt(0)) || !Character.isDigit(expression.charAt(expression.length() - 1))) {
            calculationResults.add("Error"); // Add error to results if invalid.
            return; // Exit the method.
        }

        // Stacks for numbers and operators.
        Deque<Integer> numberStack = new ArrayDeque<>(); // Stack to store numbers.
        Deque<Character> operatorStack = new ArrayDeque<>(); // Stack to store operators.
        int currentNumber = 0; // Temporary variable to build the current number.

        // Loop through each character in the expression.
        for (char c : expression.toCharArray()) {
            if (Character.isDigit(c)) { // Check if the character is a digit.
                currentNumber = currentNumber * 10 + c - '0'; // Build the number.
            } else {
                numberStack.push(currentNumber); // Push the number onto the stack.
                // Perform any pending multiplication/division.
                if (!operatorStack.isEmpty()) {
                    performOperation(numberStack, operatorStack); // Perform operation.
                }
                // Push the operator onto the stack.
                if (c == '+' || c == '-' || c == '*' || c == '/') {
                    operatorStack.push(c); // Push operator.
                } else {
                    System.out.println("Wrong input"); // Print error for wrong input.
                    return; // Exit the method.
                }
                currentNumber = 0; // Reset the current number.
            }
        }
        numberStack.push(currentNumber); // Push the last number to the stack.
        // Perform any remaining multiplication/division.
        if (!operatorStack.isEmpty()) {
            performOperation(numberStack, operatorStack); // Perform operation.
        }

        // Process addition and subtraction.
        int result = 0; // Variable to store the final result.
        while (!operatorStack.isEmpty()) {
            char op = operatorStack.pop(); // Pop an operator.
            if (op == '+') {
                result += numberStack.pop(); // Add the top number.
            } else {
                result -= numberStack.pop(); // Subtract the top number.
            }
        }
        result += numberStack.pop(); // Add the last number.
        calculationResults.add(Integer.toString(result)); // Add result to the list.
    }

    // Helper method to perform multiplication or division.
    private void performOperation(Deque<Integer> numberStack, Deque<Character> operatorStack) {
        char op = operatorStack.pop(); // Pop an operator.
        int operand2 = numberStack.pop(); // Pop the second operand.
        int operand1 = numberStack.pop(); // Pop the first operand.
        // Perform the operation based on the operator.
        switch (op) {
            case '*':
                numberStack.push(operand1 * operand2); // Multiply and push result.
                break;
            case '/':
                if (operand2 == 0) { // Check for division by zero.
                    calculationResults.add("Error"); // Add error if division by zero.
                    return; // Exit the method.
                }
                numberStack.push(operand1 / operand2); // Divide and push result.
                break;
        }
    }

    // Method to read expressions from a file.
    public void read_file(String path) {
        try {
            File file = new File(path); // Create a file object.
            FileInputStream fis = new FileInputStream(file); // Create a FileInputStream.
            StringBuilder builder = new StringBuilder(); // StringBuilder to construct expressions.
            int content; // Variable to store file content.
            // Read each character from the file.
            while ((content = fis.read()) != -1) {
                char charContent = (char) content; // Convert to char.
                if (charContent == '\n') { // Check for end of line.
                    inputExpressions.add(builder.toString()); // Add expression to list.
                    builder = new StringBuilder(); // Reset builder for new expression.
                } else if (charContent != ' ') {
                    builder.append(charContent); // Append character to builder.
                }
            }
            fis.close(); // Close the FileInputStream.
        } catch (IOException e) {
            System.out.println("An IOException occurred while reading from file: " + path); // Print error message.
        }
    }

    // Method to write results to a file.
    public void write_file(String path) {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(path)); // Create a BufferedWriter.
            for (String line : calculationResults) {
                writer.write(line); // Write a line to the file.
                writer.newLine(); // Move to a new line.
            }
            writer.close(); // Close the BufferedWriter.
        } catch (IOException e) {
            System.out.println("An error occurred while writing to file."); // Print error message.
            e.printStackTrace(); // Print stack trace.
        }
    }
}
